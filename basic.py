import math
import random
import sys
from pathlib import Path
from time import sleep

try:
    import pygame
except ModuleNotFoundError as exc:
    raise SystemExit(
        "pygame를 찾을 수 없습니다.\n"
        "가상환경을 켠 뒤 실행하세요:\n\n"
        "  source venv/bin/activate\n"
        "  python main.py\n"
    ) from exc


BLACK = (0, 0, 0)
WHITE = (245, 247, 255)
GRAY = (170, 178, 195)
RED = (235, 83, 83)
BLUE = (82, 173, 255)
GREEN = (100, 226, 160)
YELLOW = (255, 213, 92)

padWidth = 480
padHeight = 640
FPS = 60
STAGE_MAX = 5
KILLS_TO_BOSS = 45
MAX_ENEMIES_ON_SCREEN = 9
PLAYER_WIDTH = 64
PLAYER_HEIGHT = 144
GAME_BACKGROUND_PLAY_RECT = (30, 34, 1476, 956)

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "assets" / "images"
AUDIO_DIR = BASE_DIR / "assets" / "audio"
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")
AUDIO_EXTENSIONS = (".mp3", ".ogg", ".wav")

MOVE_SCANCODES = {
    "left": {4, 80},
    "right": {7, 79},
    "up": {26, 82},
    "down": {22, 81},
}

STAGES = [
    {
        "name": "1단계 안개 해협",
        "boss": "안개 지휘선",
        "trait": "3분열 탄막",
        "enemy_words": ["정찰선", "선봉선", "소형 왜선", "화살선"],
        "boss_words": ["안개탄", "화살비", "분열탄"],
        "enemy_hp": 18,
        "enemy_speed": 95,
        "spawn_ms": 980,
        "miss_damage": 7,
        "boss_hp": 260,
        "boss_shield": 0,
        "pattern": "split",
        "color": (84, 137, 170),
        "bullet_color": (255, 226, 155),
        "projectile_color": (255, 117, 92),
    },
    {
        "name": "2단계 소용돌이 해역",
        "boss": "소용돌이 장수선",
        "trait": "좌우 확산 탄막",
        "enemy_words": ["기습선", "방패선", "급류선", "창병선"],
        "boss_words": ["회오리탄", "방패 파편", "측면 포격"],
        "enemy_hp": 24,
        "enemy_speed": 108,
        "spawn_ms": 900,
        "miss_damage": 9,
        "boss_hp": 340,
        "boss_shield": 70,
        "pattern": "spread",
        "color": (90, 122, 210),
        "bullet_color": (148, 223, 255),
        "projectile_color": (146, 168, 255),
    },
    {
        "name": "3단계 화공선 돌파",
        "boss": "화공 대장선",
        "trait": "화염 분열탄",
        "enemy_words": ["화공선", "불화살선", "돌격선", "폭약선"],
        "boss_words": ["불화살", "화염 파편", "연막탄"],
        "enemy_hp": 31,
        "enemy_speed": 122,
        "spawn_ms": 820,
        "miss_damage": 11,
        "boss_hp": 430,
        "boss_shield": 110,
        "pattern": "fan",
        "color": (207, 93, 66),
        "bullet_color": (255, 194, 96),
        "projectile_color": (255, 92, 70),
    },
    {
        "name": "4단계 검은 함대",
        "boss": "검은 포위선",
        "trait": "추적 저격",
        "enemy_words": ["정예 왜선", "검은 방패선", "쌍돛선", "저격선"],
        "boss_words": ["저격탄", "검은 파편", "집중 포격"],
        "enemy_hp": 38,
        "enemy_speed": 137,
        "spawn_ms": 760,
        "miss_damage": 13,
        "boss_hp": 540,
        "boss_shield": 150,
        "pattern": "sniper",
        "color": (125, 94, 190),
        "bullet_color": (196, 169, 255),
        "projectile_color": (166, 96, 255),
    },
    {
        "name": "5단계 대장선 결전",
        "boss": "왜군 대장선",
        "trait": "방어막 재생 + 폭풍 탄막",
        "enemy_words": ["대형 왜선", "철갑선", "대포선", "대장 호위선"],
        "boss_words": ["대형 포탄", "분산 포격", "파도 탄막"],
        "enemy_hp": 46,
        "enemy_speed": 148,
        "spawn_ms": 700,
        "miss_damage": 15,
        "boss_hp": 780,
        "boss_shield": 270,
        "pattern": "storm",
        "color": (218, 72, 58),
        "bullet_color": (255, 232, 118),
        "projectile_color": (255, 73, 73),
    },
]


gamePad = None
clock = None
images = {}
sounds = {}
fonts = {}
audioEnabled = False

gameState = "menu"
paused = False
heldScancodes = set()

player = {}
bullets = []
enemies = []
enemyProjectiles = []
boss = None

stageIndex = 0
killCount = 0
score = 0
enemySpawnTimer = 0
stageBannerTimer = 0
messageTimer = 0
messageText = ""
shootCooldown = 0


def getMaximizedWindowSize():
    try:
        if hasattr(pygame.display, "get_desktop_sizes"):
            desktopSizes = pygame.display.get_desktop_sizes()
            if desktopSizes:
                width, height = desktopSizes[0]
                return max(480, width), max(640, height)

        displayInfo = pygame.display.Info()
        if displayInfo.current_w > 0 and displayInfo.current_h > 0:
            return max(480, displayInfo.current_w), max(640, displayInfo.current_h)
    except pygame.error:
        pass

    return padWidth, padHeight


def initGame():
    global gamePad, clock, padWidth, padHeight

    pygame.init()
    pygame.key.set_repeat(0)

    flags = pygame.RESIZABLE
    windowSize = (padWidth, padHeight)
    if "--windowed" not in sys.argv:
        windowSize = getMaximizedWindowSize()
        if hasattr(pygame, "MAXIMIZED"):
            flags = flags | pygame.MAXIMIZED

    gamePad = pygame.display.set_mode(windowSize, flags)
    padWidth, padHeight = gamePad.get_size()
    pygame.display.set_caption("PyShooting")
    clock = pygame.time.Clock()

    loadAssets()
    playMusic()
    showSplash()


def runGame():
    global gameState, paused, padWidth, padHeight, gamePad

    onGame = False
    while not onGame:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.VIDEORESIZE:
                padWidth = max(420, event.w)
                padHeight = max(560, event.h)
                gamePad = pygame.display.set_mode((padWidth, padHeight), pygame.RESIZABLE)
                keepPlayerInside()

            if event.type == pygame.KEYDOWN:
                handleKeyDown(event)

            if event.type == pygame.KEYUP:
                handleKeyUp(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handleMouseDown(event.pos)

        if gameState == "play" and not paused:
            updateGame(dt)

        drawScreen()
        pygame.display.update()

    pygame.quit()


def findAsset(folder, names, extensions):
    for name in names:
        for extension in extensions:
            path = folder / f"{name}{extension}"
            if path.exists():
                return path
    return None


def loadAssets():
    global images, sounds, audioEnabled

    imageNames = ["main_menu", "splash", "game_background", "player", "enemy", "mini_boss", "boss_room"]
    for stageNumber in range(1, STAGE_MAX + 1):
        imageNames += [
            f"stage{stageNumber}",
            f"enemy_stage{stageNumber}",
            f"mini_boss_stage{stageNumber}",
            f"boss_stage{stageNumber}",
            f"bullet_stage{stageNumber}",
            f"projectile_stage{stageNumber}",
        ]

    for name in imageNames:
        path = findAsset(IMAGE_DIR, [name], IMAGE_EXTENSIONS)
        if not path:
            continue
        try:
            images[name] = pygame.image.load(str(path)).convert_alpha()
        except pygame.error:
            print(f"이미지를 불러오지 못했습니다: {path}")

    try:
        pygame.mixer.init()
        audioEnabled = True
    except pygame.error:
        audioEnabled = False

    if not audioEnabled:
        return

    soundNames = ["shoot", "hit", "boss", "destroy"]
    for stageNumber in range(1, STAGE_MAX + 1):
        soundNames += [
            f"shoot_stage{stageNumber}",
            f"hit_stage{stageNumber}",
            f"boss_stage{stageNumber}",
            f"destroy_stage{stageNumber}",
        ]

    for name in soundNames:
        path = findAsset(AUDIO_DIR, [name], AUDIO_EXTENSIONS)
        if not path:
            continue
        try:
            sounds[name] = pygame.mixer.Sound(str(path))
        except pygame.error:
            print(f"효과음을 불러오지 못했습니다: {path}")


def playMusic():
    if not audioEnabled:
        return

    path = findAsset(AUDIO_DIR, ["bgm"], AUDIO_EXTENSIONS)
    if not path:
        return

    try:
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
    except pygame.error:
        print(f"배경음악을 재생하지 못했습니다: {path}")


def playSound(name, volume=0.65):
    if not audioEnabled:
        return

    sound = sounds.get(name)
    if sound is None:
        return

    sound.set_volume(volume)
    sound.play()


def playStageSound(kind, volume=0.65):
    stageNumber = stageIndex + 1
    playSound(f"{kind}_stage{stageNumber}", volume)
    if f"{kind}_stage{stageNumber}" not in sounds:
        playSound(kind, volume)


def getFont(size, bold=False):
    key = (size, bold)
    if key in fonts:
        return fonts[key]

    candidates = [
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "/Library/Fonts/NanumGothic.ttf",
        "C:/Windows/Fonts/malgun.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    ]

    for candidate in candidates:
        if Path(candidate).exists():
            font = pygame.font.Font(candidate, size)
            font.set_bold(bold)
            fonts[key] = font
            return font

    fontPath = pygame.font.match_font("applesdgothicneo,nanumgothic,malgungothic,arialunicode")
    if fontPath:
        font = pygame.font.Font(fontPath, size)
    else:
        font = pygame.font.Font(None, size)
    font.set_bold(bold)
    fonts[key] = font
    return font


def drawText(text, size, color, x, y, center=False, bold=False):
    font = getFont(size, bold)
    image = font.render(text, True, color)
    rect = image.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    gamePad.blit(image, rect)
    return rect


def getCoverRect(image):
    scale = max(padWidth / image.get_width(), padHeight / image.get_height())
    width = int(image.get_width() * scale)
    height = int(image.get_height() * scale)
    rect = pygame.Rect(0, 0, width, height)
    rect.center = (padWidth // 2, padHeight // 2)
    return rect, scale


def drawCover(image):
    rect, scale = getCoverRect(image)
    width, height = rect.size
    scaled = pygame.transform.smoothscale(image, (width, height))
    gamePad.blit(scaled, rect)
    return rect, scale


def getHudHeight():
    return 98 if padWidth < 720 else 82


def getPlayArea():
    background = getStageImage("stage")
    if background:
        drawnRect, scale = getCoverRect(background)
        sourceX, sourceY, sourceW, sourceH = GAME_BACKGROUND_PLAY_RECT
        area = pygame.Rect(
            drawnRect.left + int(sourceX * scale),
            drawnRect.top + int(sourceY * scale),
            int(sourceW * scale),
            int(sourceH * scale),
        )
        return area.clip(pygame.Rect(0, 0, padWidth, padHeight))

    top = getHudHeight() + 12
    return pygame.Rect(8, top, padWidth - 16, padHeight - top - 12)


def showSplash():
    splash = images.get("splash")
    if splash:
        drawCover(splash)
    else:
        gamePad.fill(BLACK)
        drawText("PyShooting", 48, WHITE, padWidth // 2, padHeight // 2 - 24, True, True)
        drawText("거북선 전쟁", 24, GRAY, padWidth // 2, padHeight // 2 + 28, True)
    pygame.display.update()
    sleep(0.35)


def getCurrentStage():
    return STAGES[stageIndex]


def getStageImage(kind):
    stageNumber = stageIndex + 1

    if kind == "stage":
        return images.get(f"stage{stageNumber}") or images.get("game_background")
    if kind == "enemy":
        return images.get(f"enemy_stage{stageNumber}") or images.get("enemy")
    if kind == "boss":
        return (
            images.get(f"mini_boss_stage{stageNumber}")
            or images.get(f"boss_stage{stageNumber}")
            or images.get("mini_boss")
        )
    if kind == "bullet":
        return images.get(f"bullet_stage{stageNumber}")
    if kind == "projectile":
        return images.get(f"projectile_stage{stageNumber}")

    return None


def handleKeyDown(event):
    global gameState, paused

    if getattr(event, "scancode", None) is not None:
        heldScancodes.add(event.scancode)

    if gameState == "menu":
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            startGame()
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        return

    if gameState in ("gameover", "clear"):
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            startGame()
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        return

    if event.key == pygame.K_ESCAPE:
        gameState = "menu"
        return

    if event.key == pygame.K_p:
        paused = not paused
        return

    if gameState != "play" or paused:
        return

    if event.key == pygame.K_SPACE:
        shootPlayerBullet()


def handleKeyUp(event):
    if getattr(event, "scancode", None) is not None:
        heldScancodes.discard(event.scancode)


def handleMouseDown(pos):
    if gameState == "menu":
        if getStartButtonRect().collidepoint(pos):
            startGame()
        return

    if gameState in ("gameover", "clear"):
        startGame()
        return

    if gameState == "play" and not paused:
        shootPlayerBullet()


def startGame():
    global gameState, paused, stageIndex, killCount, score, enemySpawnTimer
    global stageBannerTimer, messageTimer, messageText, shootCooldown
    global bullets, enemies, enemyProjectiles, boss, player

    gameState = "play"
    paused = False
    stageIndex = 0
    killCount = 0
    score = 0
    enemySpawnTimer = 0
    stageBannerTimer = 2.0
    messageTimer = 0
    messageText = ""
    shootCooldown = 0
    bullets = []
    enemies = []
    enemyProjectiles = []
    boss = None

    player = {
        "rect": pygame.Rect(0, 0, PLAYER_WIDTH, PLAYER_HEIGHT),
        "maxHp": 140,
        "hp": 140.0,
        "speed": 360,
    }
    playArea = getPlayArea()
    player["rect"].center = (playArea.centerx, playArea.bottom - 72)
    keepPlayerInside()


def nextStage():
    global stageIndex, killCount, boss, enemies, bullets, enemyProjectiles
    global stageBannerTimer, gameState

    stageIndex += 1
    if stageIndex >= STAGE_MAX:
        gameState = "clear"
        return

    killCount = 0
    boss = None
    enemies = []
    bullets = []
    enemyProjectiles = []
    stageBannerTimer = 2.0


def updateGame(dt):
    global enemySpawnTimer, stageBannerTimer, messageTimer, shootCooldown

    stageBannerTimer = max(0, stageBannerTimer - dt)
    messageTimer = max(0, messageTimer - dt)
    shootCooldown = max(0, shootCooldown - dt)

    updatePlayer(dt)
    updateBullets(dt)
    updateEnemies(dt)
    updateBoss(dt)
    updateEnemyProjectiles(dt)
    checkCollisions()

    if player["hp"] <= 0:
        endGame(False)


def updatePlayer(dt):
    keys = pygame.key.get_pressed()
    moveX = 0
    moveY = 0

    if keys[pygame.K_LEFT] or keys[pygame.K_a] or heldScancodes & MOVE_SCANCODES["left"]:
        moveX -= 1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d] or heldScancodes & MOVE_SCANCODES["right"]:
        moveX += 1
    if keys[pygame.K_UP] or keys[pygame.K_w] or heldScancodes & MOVE_SCANCODES["up"]:
        moveY -= 1
    if keys[pygame.K_DOWN] or keys[pygame.K_s] or heldScancodes & MOVE_SCANCODES["down"]:
        moveY += 1

    if moveX != 0 or moveY != 0:
        length = math.sqrt(moveX * moveX + moveY * moveY)
        player["rect"].x += int(moveX / length * player["speed"] * dt)
        player["rect"].y += int(moveY / length * player["speed"] * dt)

    keepPlayerInside()


def keepPlayerInside():
    if not player:
        return

    rect = player["rect"]
    playArea = getPlayArea()
    topLimit = max(playArea.top + 8, getHudHeight() + 12)
    rect.left = max(playArea.left + 8, rect.left)
    rect.right = min(playArea.right - 8, rect.right)
    rect.top = max(topLimit, rect.top)
    rect.bottom = min(playArea.bottom - 8, rect.bottom)


def shootPlayerBullet():
    global shootCooldown

    if not player or shootCooldown > 0:
        return

    stage = getCurrentStage()
    rect = player["rect"]
    speed = -620
    damage = 18
    color = stage["bullet_color"]
    radius = 7

    makeBullet(rect.centerx, rect.top - 8, 0, speed, damage, radius, color)

    shootCooldown = 0.28
    playStageSound("shoot", 0.5)


def makeBullet(x, y, vx, vy, damage, radius, color):
    bullets.append(
        {
            "x": float(x),
            "y": float(y),
            "vx": float(vx),
            "vy": float(vy),
            "damage": float(damage),
            "radius": radius,
            "color": color,
        }
    )


def updateBullets(dt):
    playArea = getPlayArea()
    for bullet in bullets[:]:
        bullet["x"] += bullet["vx"] * dt
        bullet["y"] += bullet["vy"] * dt
        if (
            bullet["y"] < playArea.top - 60
            or bullet["x"] < playArea.left - 60
            or bullet["x"] > playArea.right + 60
        ):
            bullets.remove(bullet)


def updateEnemies(dt):
    global enemySpawnTimer

    if boss is not None:
        return

    playArea = getPlayArea()
    for enemy in enemies[:]:
        enemy["age"] += dt
        enemy["rect"].y += int(enemy["speed"] * dt)
        enemy["rect"].x += int(math.sin(enemy["age"] * 2.6) * enemy["drift"] * dt)
        enemy["rect"].left = max(playArea.left + 6, enemy["rect"].left)
        enemy["rect"].right = min(playArea.right - 6, enemy["rect"].right)

        if enemy["rect"].top > playArea.bottom + 40:
            enemies.remove(enemy)
            damagePlayer(enemy["miss_damage"])

    enemySpawnTimer += dt * 1000
    stage = getCurrentStage()
    spawnMs = stage["spawn_ms"]

    if killCount >= KILLS_TO_BOSS:
        spawnBoss()
        return

    if enemySpawnTimer < spawnMs or len(enemies) >= MAX_ENEMIES_ON_SCREEN:
        return

    enemySpawnTimer = 0
    createEnemy()


def createEnemy():
    stage = getCurrentStage()
    playArea = getPlayArea()
    spawnTop = max(playArea.top, getHudHeight() + 10)
    width = random.randint(72, 94)
    height = random.randint(42, 54)
    minX = playArea.left + width // 2 + 8
    maxX = max(minX, playArea.right - width // 2 - 8)
    x = random.randint(minX, maxX)
    rect = pygame.Rect(0, 0, width, height)
    rect.center = (x, spawnTop - height)

    enemies.append(
        {
            "rect": rect,
            "hp": float(stage["enemy_hp"]),
            "maxHp": float(stage["enemy_hp"]),
            "speed": stage["enemy_speed"] * random.uniform(0.85, 1.18),
            "word": random.choice(stage["enemy_words"]),
            "drift": random.uniform(-55, 55),
            "age": random.random() * 10,
            "damage": 16 + stageIndex * 4,
            "miss_damage": stage["miss_damage"],
        }
    )


def spawnBoss():
    global boss, enemies, enemyProjectiles, messageText, messageTimer

    stage = getCurrentStage()
    playArea = getPlayArea()
    width = 300 if stageIndex == STAGE_MAX - 1 else 230 + stageIndex * 18
    height = 126 if stageIndex == STAGE_MAX - 1 else 96 + stageIndex * 8
    rect = pygame.Rect(0, 0, width, height)
    rect.center = (playArea.centerx, playArea.top - height)

    boss = {
        "rect": rect,
        "hp": float(stage["boss_hp"]),
        "maxHp": float(stage["boss_hp"]),
        "shield": float(stage["boss_shield"]),
        "maxShield": float(stage["boss_shield"]),
        "age": 0.0,
        "shotTimer": 0.9,
        "burstTimer": 2.2,
        "restoreTimer": 0.0,
    }

    enemies = []
    enemyProjectiles = []
    messageText = f"{stage['boss']} 등장"
    messageTimer = 2.0
    playStageSound("boss", 0.8)


def updateBoss(dt):
    if boss is None:
        return

    stage = getCurrentStage()
    rect = boss["rect"]
    playArea = getPlayArea()
    boss["age"] += dt

    targetY = max(playArea.top + 92, getHudHeight() + 36)
    rect.y += int((targetY - rect.y) * min(1, dt * 2.8))

    centerX = playArea.centerx
    sway = min(260, playArea.width * 0.22)
    pattern = stage["pattern"]

    if pattern == "sniper":
        playerX = player["rect"].centerx
        rect.centerx += int(max(-180 * dt, min(180 * dt, playerX - rect.centerx)))
    elif pattern == "storm":
        rect.centerx = int(centerX + math.sin(boss["age"] * 2.5) * sway + math.sin(boss["age"] * 5) * 35)
    else:
        rect.centerx = int(centerX + math.sin(boss["age"] * (1.2 + stageIndex * 0.18)) * sway)

    rect.left = max(playArea.left + 12, rect.left)
    rect.right = min(playArea.right - 12, rect.right)

    if stageIndex == STAGE_MAX - 1 and boss["shield"] <= 0:
        boss["restoreTimer"] += dt
        if boss["restoreTimer"] >= 8.0:
            boss["shield"] = boss["maxShield"] * 0.45
            boss["restoreTimer"] = 0

    boss["shotTimer"] -= dt
    boss["burstTimer"] -= dt

    if boss["shotTimer"] <= 0:
        boss["shotTimer"] = max(0.38, 1.1 - stageIndex * 0.11)
        shootBossProjectile(0, aimed=True)

    if boss["burstTimer"] <= 0:
        boss["burstTimer"] = max(1.3, 2.6 - stageIndex * 0.15)
        shootBossBurst()


def shootBossProjectile(xOffset, aimed=False, angleOffset=0):
    stage = getCurrentStage()
    rect = boss["rect"]
    startX = rect.centerx + xOffset
    startY = rect.bottom - 8
    speed = 210 + stageIndex * 28

    if aimed:
        dx = player["rect"].centerx - startX
        dy = player["rect"].centery - startY
        length = max(1, math.sqrt(dx * dx + dy * dy))
        vx = dx / length * speed
        vy = dy / length * speed
    else:
        vx = angleOffset
        vy = speed

    enemyProjectiles.append(
        {
            "x": float(startX),
            "y": float(startY),
            "vx": float(vx),
            "vy": float(vy),
            "radius": 18 + stageIndex * 2,
            "damage": 12 + stageIndex * 3,
            "word": random.choice(stage["boss_words"]),
            "split": 1 if stage["pattern"] in ("split", "fan", "storm") else 0,
            "age": 0.0,
            "splitDone": False,
            "color": stage["projectile_color"],
        }
    )


def shootBossBurst():
    pattern = getCurrentStage()["pattern"]

    if pattern == "spread":
        offsets = [-90, -45, 0, 45, 90]
    elif pattern == "fan":
        offsets = [-150, -95, -45, 45, 95, 150]
    elif pattern == "sniper":
        offsets = [-40, 0, 40]
    elif pattern == "storm":
        offsets = [-180, -120, -60, 0, 60, 120, 180]
    else:
        offsets = [-70, 0, 70]

    for offset in offsets:
        shootBossProjectile(offset * 0.35, aimed=False, angleOffset=offset)


def updateEnemyProjectiles(dt):
    playArea = getPlayArea()
    for projectile in enemyProjectiles[:]:
        projectile["age"] += dt
        projectile["x"] += projectile["vx"] * dt
        projectile["y"] += projectile["vy"] * dt

        if projectile["split"] > 0 and not projectile["splitDone"] and projectile["age"] > 0.75:
            projectile["splitDone"] = True
            splitProjectile(projectile)

        if (
            projectile["x"] < playArea.left - 80
            or projectile["x"] > playArea.right + 80
            or projectile["y"] < playArea.top - 80
            or projectile["y"] > playArea.bottom + 80
        ):
            enemyProjectiles.remove(projectile)


def splitProjectile(projectile):
    for vx in (-120, 0, 120):
        enemyProjectiles.append(
            {
                "x": projectile["x"],
                "y": projectile["y"],
                "vx": projectile["vx"] * 0.45 + vx,
                "vy": max(170, projectile["vy"] * 0.9),
                "radius": max(12, int(projectile["radius"] * 0.62)),
                "damage": projectile["damage"] * 0.58,
                "word": projectile["word"],
                "split": projectile["split"] - 1,
                "age": 0.0,
                "splitDone": False,
                "color": projectile["color"],
            }
        )


def checkCollisions():
    checkBulletEnemyCollisions()
    checkBulletBossCollisions()
    checkPlayerEnemyCollisions()
    checkPlayerProjectileCollisions()


def checkBulletEnemyCollisions():
    global killCount, score

    for bullet in bullets[:]:
        bulletRect = getCircleRect(bullet["x"], bullet["y"], bullet["radius"])
        hitEnemy = None

        for enemy in enemies:
            if enemy["rect"].colliderect(bulletRect):
                hitEnemy = enemy
                break

        if hitEnemy is None:
            continue

        if bullet in bullets:
            bullets.remove(bullet)

        hitEnemy["hp"] -= bullet["damage"]
        if hitEnemy["hp"] <= 0:
            enemies.remove(hitEnemy)
            killCount += 1
            score += 100 + stageIndex * 25
            playStageSound("destroy", 0.45)


def checkBulletBossCollisions():
    global boss, score

    if boss is None:
        return

    for bullet in bullets[:]:
        bulletRect = getCircleRect(bullet["x"], bullet["y"], bullet["radius"])
        if not boss["rect"].colliderect(bulletRect):
            continue

        if bullet in bullets:
            bullets.remove(bullet)

        damageBoss(bullet["damage"])

        if boss is not None and boss["hp"] <= 0:
            score += 1200 + stageIndex * 400
            nextStage()
            return


def checkPlayerEnemyCollisions():
    for enemy in enemies[:]:
        if enemy["rect"].colliderect(player["rect"]):
            enemies.remove(enemy)
            damagePlayer(enemy["damage"])


def checkPlayerProjectileCollisions():
    for projectile in enemyProjectiles[:]:
        rect = getCircleRect(projectile["x"], projectile["y"], projectile["radius"])
        if player["rect"].colliderect(rect):
            enemyProjectiles.remove(projectile)
            damagePlayer(projectile["damage"])


def getCircleRect(x, y, radius):
    rect = pygame.Rect(0, 0, radius * 2, radius * 2)
    rect.center = (int(x), int(y))
    return rect


def damageBoss(amount):
    if boss is None:
        return

    remain = amount
    if boss["shield"] > 0:
        shieldDamage = min(boss["shield"], remain)
        boss["shield"] -= shieldDamage
        remain -= shieldDamage
        if boss["shield"] <= 0:
            boss["restoreTimer"] = 0

    if remain > 0:
        boss["hp"] = max(0, boss["hp"] - remain)


def damagePlayer(amount):
    player["hp"] = max(0, player["hp"] - amount)
    playStageSound("hit", 0.65)


def endGame(clear):
    global gameState
    gameState = "clear" if clear else "gameover"


def getStartButtonRect():
    menuImage = images.get("main_menu")
    if menuImage:
        sourceRect = (898, 584, 386, 92)
        scale = max(padWidth / menuImage.get_width(), padHeight / menuImage.get_height())
        width = int(menuImage.get_width() * scale)
        height = int(menuImage.get_height() * scale)
        left = (padWidth - width) // 2
        top = (padHeight - height) // 2
        rect = pygame.Rect(
            left + int(sourceRect[0] * scale),
            top + int(sourceRect[1] * scale),
            int(sourceRect[2] * scale),
            int(sourceRect[3] * scale),
        )
        if rect.colliderect(pygame.Rect(0, 0, padWidth, padHeight)):
            return rect

    rect = pygame.Rect(0, 0, min(380, int(padWidth * 0.72)), 68)
    rect.center = (padWidth // 2, int(padHeight * 0.64))
    return rect


def drawScreen():
    if gameState == "menu":
        drawMenu()
    elif gameState == "play":
        drawGame()
    elif gameState == "gameover":
        drawEndScreen(False)
    elif gameState == "clear":
        drawEndScreen(True)


def drawMenu():
    menuImage = images.get("main_menu")
    if menuImage:
        drawCover(menuImage)
    else:
        drawSeaBackground()
        drawText("PyShooting", 52, WHITE, padWidth // 2, int(padHeight * 0.28), True, True)
        drawText("거북선 전쟁", 26, YELLOW, padWidth // 2, int(padHeight * 0.36), True, True)

    startRect = getStartButtonRect()
    mousePos = pygame.mouse.get_pos()
    hovered = startRect.collidepoint(mousePos)
    buttonColor = (130, 80, 34) if not hovered else (165, 103, 45)
    borderColor = (255, 209, 117)

    pygame.draw.rect(gamePad, buttonColor, startRect, border_radius=8)
    pygame.draw.rect(gamePad, borderColor, startRect, 3, border_radius=8)
    drawText("게임 시작", max(24, startRect.height // 3), WHITE, startRect.centerx, startRect.centery, True, True)


def drawGame():
    drawStageBackground()

    for bullet in bullets:
        drawBullet(bullet)

    for enemy in enemies:
        drawEnemy(enemy)

    if boss is not None:
        drawBoss()

    for projectile in enemyProjectiles:
        drawEnemyProjectile(projectile)

    drawPlayer()
    drawHud()

    if stageBannerTimer > 0:
        stage = getCurrentStage()
        drawText(stage["name"], 36, WHITE, padWidth // 2, padHeight // 2 - 30, True, True)
        drawText(f"미니보스: {stage['boss']} / {stage['trait']}", 21, YELLOW, padWidth // 2, padHeight // 2 + 12, True)

    if messageTimer > 0:
        drawText(messageText, 30, YELLOW, padWidth // 2, int(padHeight * 0.72), True, True)

    if paused:
        shade = pygame.Surface((padWidth, padHeight), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 145))
        gamePad.blit(shade, (0, 0))
        drawText("일시정지", 48, WHITE, padWidth // 2, padHeight // 2 - 20, True, True)


def drawEndScreen(clear):
    drawSeaBackground()
    title = "승리했습니다" if clear else "게임 오버"
    detail = "5개의 스테이지를 모두 돌파했습니다." if clear else "다시 도전해보세요."

    drawText(title, 52, WHITE, padWidth // 2, padHeight // 2 - 70, True, True)
    drawText(detail, 22, GRAY, padWidth // 2, padHeight // 2 - 20, True)
    drawText(f"점수 {score:,}", 30, YELLOW, padWidth // 2, padHeight // 2 + 34, True, True)


def drawSeaBackground():
    gamePad.fill((11, 20, 34))
    for y in range(0, padHeight, 22):
        color = (12, 36 + min(95, y // 8), 62 + min(90, y // 10))
        pygame.draw.rect(gamePad, color, (0, y, padWidth, 22))

    for i in range(14):
        x = (i * 127 + pygame.time.get_ticks() // 18) % (padWidth + 80) - 40
        y = int(padHeight * 0.28) + i * 37 % max(1, int(padHeight * 0.65))
        pygame.draw.arc(gamePad, (52, 117, 150), (x, y, 80, 16), 0, math.pi, 1)


def drawStageBackground():
    image = getStageImage("stage")
    if image:
        drawCover(image)
        shade = pygame.Surface((padWidth, padHeight), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 34))
        gamePad.blit(shade, (0, 0))
        return

    drawSeaBackground()
    stage = getCurrentStage()
    tint = pygame.Surface((padWidth, padHeight), pygame.SRCALPHA)
    color = stage["color"]
    tint.fill((color[0], color[1], color[2], 42))
    gamePad.blit(tint, (0, 0))


def drawPlayer():
    rect = player["rect"]
    image = images.get("player")

    if image:
        scaled = pygame.transform.smoothscale(image, rect.size)
        gamePad.blit(scaled, rect)
    else:
        pygame.draw.polygon(
            gamePad,
            (53, 158, 122),
            [(rect.centerx, rect.top), (rect.left, rect.bottom), (rect.right, rect.bottom)],
        )
        pygame.draw.polygon(
            gamePad,
            (235, 246, 240),
            [(rect.centerx, rect.top + 8), (rect.left + 10, rect.bottom - 8), (rect.right - 10, rect.bottom - 8)],
            2,
        )
        pygame.draw.circle(gamePad, YELLOW, (rect.centerx, rect.top + 22), 7)

def drawBullet(bullet):
    image = getStageImage("bullet")
    rect = getCircleRect(bullet["x"], bullet["y"], bullet["radius"])

    if image:
        scaled = pygame.transform.smoothscale(image, rect.inflate(10, 10).size)
        gamePad.blit(scaled, scaled.get_rect(center=rect.center))
        return

    pygame.draw.circle(gamePad, bullet["color"], rect.center, bullet["radius"])
    pygame.draw.circle(gamePad, WHITE, rect.center, max(2, bullet["radius"] - 4))


def drawEnemy(enemy):
    rect = enemy["rect"]
    image = getStageImage("enemy")

    if image:
        scaled = pygame.transform.smoothscale(image, rect.size)
        gamePad.blit(scaled, rect)
    else:
        pygame.draw.rect(gamePad, (82, 40, 50), rect, border_radius=7)
        pygame.draw.rect(gamePad, RED, rect, 2, border_radius=7)

    drawText(enemy["word"], 16, WHITE, rect.centerx, rect.centery - 2, True, True)

    hpRect = pygame.Rect(rect.left + 8, rect.bottom + 4, rect.width - 16, 5)
    pygame.draw.rect(gamePad, (42, 34, 38), hpRect, border_radius=2)
    fill = hpRect.copy()
    fill.width = int(hpRect.width * max(0, enemy["hp"] / enemy["maxHp"]))
    pygame.draw.rect(gamePad, YELLOW, fill, border_radius=2)


def drawBoss():
    stage = getCurrentStage()
    rect = boss["rect"]
    image = getStageImage("boss")

    if image:
        scaled = pygame.transform.smoothscale(image, rect.size)
        gamePad.blit(scaled, rect)
    else:
        pygame.draw.rect(gamePad, (62, 37, 48), rect, border_radius=10)
        pygame.draw.rect(gamePad, stage["color"], rect, 4, border_radius=10)
        pygame.draw.circle(gamePad, RED, (rect.centerx, rect.centery), min(rect.width, rect.height) // 4)

    drawText(stage["boss"], 22, WHITE, rect.centerx, rect.centery - 12, True, True)
    drawText(stage["trait"], 16, YELLOW, rect.centerx, rect.centery + 18, True)


def drawEnemyProjectile(projectile):
    image = getStageImage("projectile")
    rect = getCircleRect(projectile["x"], projectile["y"], projectile["radius"])

    if image:
        scaled = pygame.transform.smoothscale(image, rect.inflate(12, 12).size)
        gamePad.blit(scaled, scaled.get_rect(center=rect.center))
    else:
        pygame.draw.circle(gamePad, (77, 30, 42), rect.center, projectile["radius"])
        pygame.draw.circle(gamePad, projectile["color"], rect.center, projectile["radius"], 2)

    drawText(projectile["word"], max(12, projectile["radius"] // 2), WHITE, rect.centerx, rect.centery, True, True)


def drawHud():
    hudHeight = getHudHeight()
    panel = pygame.Surface((padWidth, hudHeight), pygame.SRCALPHA)
    panel.fill((5, 9, 17, 185))
    gamePad.blit(panel, (0, 0))

    stage = getCurrentStage()
    drawText(stage["name"], 20, WHITE, 14, 9, False, True)
    drawText(f"점수 {score:,}", 16, GRAY, 14, 36)

    hpW = min(190, max(120, padWidth // 4))
    hpRect = pygame.Rect(14, hudHeight - 22, hpW, 12)
    pygame.draw.rect(gamePad, (45, 35, 40), hpRect, border_radius=6)
    hpFill = hpRect.copy()
    hpFill.width = int(hpRect.width * max(0, player["hp"] / player["maxHp"]))
    pygame.draw.rect(gamePad, GREEN if player["hp"] > 45 else RED, hpFill, border_radius=6)
    pygame.draw.rect(gamePad, WHITE, hpRect, 1, border_radius=6)
    drawText(f"체력 {int(player['hp'])}/{player['maxHp']}", 14, WHITE, hpRect.right + 8, hpRect.centery - 9)

    centerX = padWidth // 2
    if boss is None:
        drawText(f"격침 {killCount}/{KILLS_TO_BOSS}", 22, YELLOW, centerX, 17, True, True)
    else:
        drawText("미니보스 교전", 22, RED, centerX, 17, True, True)
        bossHpRect = pygame.Rect(centerX - 130, 45, 260, 12)
        pygame.draw.rect(gamePad, (48, 29, 35), bossHpRect, border_radius=6)
        bossFill = bossHpRect.copy()
        bossFill.width = int(bossHpRect.width * max(0, boss["hp"] / boss["maxHp"]))
        pygame.draw.rect(gamePad, RED, bossFill, border_radius=6)
        pygame.draw.rect(gamePad, WHITE, bossHpRect, 1, border_radius=6)
        if boss["maxShield"] > 0:
            shieldRect = bossHpRect.move(0, 17)
            pygame.draw.rect(gamePad, (29, 43, 55), shieldRect, border_radius=6)
            shieldFill = shieldRect.copy()
            shieldFill.width = int(shieldRect.width * max(0, boss["shield"] / boss["maxShield"]))
            pygame.draw.rect(gamePad, BLUE, shieldFill, border_radius=6)


if __name__ == "__main__":
    initGame()
    runGame()
