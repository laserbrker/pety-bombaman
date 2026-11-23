"""Bomber de escritorio.

Sprites de las hojas que Jonny dejo en Descargas, copiadas en art/.
No borra iconos: la explosion es un dibujo y suelta un item.
Clic izquierdo: se enoja y trae Grok al frente.
Clic derecho: se va.
A los minutos 50 dice hurry up.
"""

from __future__ import annotations

import ctypes
import faulthandler
import math
import os
import random
import struct
import subprocess
import sys
import time
import traceback
import wave
import winsound
from ctypes import wintypes
from pathlib import Path

def prepare_tcl() -> None:
    root = Path(sys.executable).resolve().parent
    tcl = root / "tcl" / "tcl8.6"
    tk = root / "tcl" / "tk8.6"
    if tcl.is_dir():
        os.environ.setdefault("TCL_LIBRARY", str(tcl))
    if tk.is_dir():
        os.environ.setdefault("TK_LIBRARY", str(tk))


prepare_tcl()

from PIL import Image, ImageDraw, ImageOps, ImageTk

HERE = Path(__file__).resolve().parent
LOG = HERE / "pet.log"
STATUS = HERE / "status.txt"
NOW = HERE / "now.png"
WAV = HERE / "boom.wav"
HURRY = HERE / "hurry.mp3"
ART = HERE / "art"
SND = HERE / "snd"
PLACE = SND / "place.wav"
EXPLODE = SND / "explode.wav"
LISTO = SND / "listo.wav"
GRITO = SND / "grito.wav"
CAIGO = SND / "caigo.wav"
STEP_H = SND / "step_h.wav"
STEP_V = SND / "step_v.wav"
ICON = HERE / "pety.ico"
STOP = HERE / "STOP"
GROK = Path.home() / ".grok" / "bin" / "grok.exe"

SCALE = 3
FPS_MS = 90
WALK = 90
MAGENTA = (255, 0, 255)
KEY = "#FF00FF"

OUT = (22, 18, 32, 255)
WHITE = (250, 250, 252, 255)
SHADE = (196, 204, 224, 255)
PINK = (255, 92, 168, 255)
PINK_D = (214, 48, 112, 255)
EYE = (24, 18, 32, 255)
ANT = (255, 214, 64, 255)
ANT_L = (255, 244, 190, 255)
BLUE = (46, 104, 232, 255)
BLUE_D = (24, 62, 168, 255)
BLACK = (18, 16, 22, 255)
RED = (230, 48, 42, 255)
ORANGE = (255, 140, 32, 255)
YELLOW = (255, 228, 96, 255)
CREAM = (255, 248, 220, 255)
DARKRED = (150, 32, 24, 255)
GREEN = (64, 190, 96, 255)

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
winmm = ctypes.WinDLL("winmm")
winmm.mciSendStringW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.UINT, wintypes.HANDLE]
winmm.mciSendStringW.restype = wintypes.DWORD

HWND_BOTTOM = 1
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TRANSPARENT = 0x00000020
GW_HWNDPREV = 3
DWMWA_CLOAKED = 14

user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.FindWindowW.restype = wintypes.HWND
user32.FindWindowExW.argtypes = [wintypes.HWND, wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.FindWindowExW.restype = wintypes.HWND
user32.GetParent.argtypes = [wintypes.HWND]
user32.GetParent.restype = wintypes.HWND
user32.SetWindowPos.argtypes = [
    wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int, ctypes.c_uint,
]
user32.SetWindowPos.restype = wintypes.BOOL
user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetWindowLongW.restype = ctypes.c_long
user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
user32.SetWindowLongW.restype = ctypes.c_long
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetClassNameW.restype = ctypes.c_int
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.c_void_p]
user32.GetWindowRect.restype = wintypes.BOOL
user32.GetWindow.argtypes = [wintypes.HWND, ctypes.c_uint]
user32.GetWindow.restype = wintypes.HWND
user32.EnumWindows.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
user32.EnumWindows.restype = wintypes.BOOL
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, ctypes.c_size_t, ctypes.c_void_p]
user32.SendMessageW.restype = ctypes.c_ssize_t
user32.LoadImageW.argtypes = [
    wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT,
    ctypes.c_int, ctypes.c_int, wintypes.UINT,
]
user32.LoadImageW.restype = wintypes.HANDLE
user32.SetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
user32.SetWindowTextW.restype = wintypes.BOOL
user32.SendMessageTimeoutW.argtypes = [
    wintypes.HWND, wintypes.UINT, ctypes.c_size_t, ctypes.c_void_p,
    wintypes.UINT, wintypes.UINT, ctypes.POINTER(ctypes.c_size_t),
]
user32.SendMessageTimeoutW.restype = ctypes.c_ssize_t
user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.c_void_p]
user32.ClientToScreen.restype = wintypes.BOOL
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.ShowWindow.restype = wintypes.BOOL
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.GetForegroundWindow.argtypes = []
user32.GetForegroundWindow.restype = wintypes.HWND
user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
user32.AttachThreadInput.restype = wintypes.BOOL
user32.IsIconic.argtypes = [wintypes.HWND]
user32.IsIconic.restype = wintypes.BOOL
user32.IsWindow.argtypes = [wintypes.HWND]
user32.IsWindow.restype = wintypes.BOOL
user32.SystemParametersInfoW.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]
user32.SystemParametersInfoW.restype = wintypes.BOOL

kernel32.GetCurrentProcess.restype = wintypes.HANDLE
kernel32.GetCurrentThreadId.restype = wintypes.DWORD
kernel32.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
kernel32.SetPriorityClass.restype = wintypes.BOOL
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.VirtualAllocEx.argtypes = [
    wintypes.HANDLE, ctypes.c_void_p, ctypes.c_size_t, wintypes.DWORD, wintypes.DWORD,
]
kernel32.VirtualAllocEx.restype = ctypes.c_void_p
kernel32.VirtualFreeEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_size_t, wintypes.DWORD]
kernel32.VirtualFreeEx.restype = wintypes.BOOL
kernel32.ReadProcessMemory.argtypes = [
    wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p,
]
kernel32.ReadProcessMemory.restype = wintypes.BOOL
kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.CreateMutexW.restype = wintypes.HANDLE
kernel32.GetLastError.restype = wintypes.DWORD


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long), ("top", ctypes.c_long),
        ("right", ctypes.c_long), ("bottom", ctypes.c_long),
    ]


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
user32.GetCursorPos.restype = wintypes.BOOL
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.GetAsyncKeyState.restype = ctypes.c_short
user32.GetDoubleClickTime.restype = wintypes.UINT


WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def beat(msg: str) -> None:
    try:
        (HERE / "beat.txt").write_text(msg, encoding="utf-8")
    except OSError:
        pass


def log(msg: str) -> None:
    try:
        with LOG.open("a", encoding="utf-8") as handle:
            handle.write(time.strftime("%H:%M:%S ") + msg + "\n")
    except OSError:
        pass


def scale(image: Image.Image) -> Image.Image:
    return image.resize((image.width * SCALE, image.height * SCALE), Image.Resampling.NEAREST)


def blank(w: int, h: int) -> Image.Image:
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def draw_front(step: int, mood: str) -> Image.Image:
    image = blank(40, 40)
    draw = ImageDraw.Draw(image)
    bob = 0 if step == 0 else 1
    draw.ellipse((8, 9 + bob, 31, 32 + bob), fill=OUT)
    draw.ellipse((9, 10 + bob, 30, 31 + bob), fill=WHITE)
    draw.ellipse((18, 18 + bob, 29, 30 + bob), fill=SHADE)
    draw.rectangle((19, 4 + bob, 21, 12 + bob), fill=OUT)
    draw.ellipse((15, 1 + bob, 25, 10 + bob), fill=OUT)
    draw.ellipse((16, 2 + bob, 24, 9 + bob), fill=ANT)
    draw.point((18, 3 + bob), fill=ANT_L)
    if mood == "dead":
        return image
    if mood == "mad":
        draw.line((11, 14 + bob, 16, 16 + bob), fill=EYE, width=1)
        draw.line((28, 14 + bob, 23, 16 + bob), fill=EYE, width=1)
        draw.rectangle((12, 17 + bob, 16, 20 + bob), fill=EYE)
        draw.rectangle((23, 17 + bob, 27, 20 + bob), fill=EYE)
        draw.rectangle((17, 24 + bob, 22, 27 + bob), fill=RED)
    else:
        closed = mood == "blink"
        eye_h = 1 if closed else 4
        draw.rectangle((12, 17 + bob, 16, 17 + eye_h + bob), fill=EYE)
        draw.rectangle((23, 17 + bob, 27, 17 + eye_h + bob), fill=EYE)
        if not closed:
            draw.point((13, 18 + bob), fill=WHITE)
            draw.point((24, 18 + bob), fill=WHITE)
        draw.rectangle((9, 22 + bob, 12, 24 + bob), fill=PINK)
        draw.rectangle((27, 22 + bob, 30, 24 + bob), fill=PINK)
        draw.point((16, 25 + bob), fill=PINK_D)
        draw.rectangle((17, 26 + bob, 22, 27 + bob), fill=PINK_D)
        draw.point((23, 25 + bob), fill=PINK_D)
    if mood == "wave":
        draw.ellipse((28, 10 + bob, 36, 18 + bob), fill=OUT)
        draw.ellipse((29, 11 + bob, 35, 17 + bob), fill=WHITE)
        draw.rectangle((30, 16 + bob, 33, 22 + bob), fill=BLUE)
        draw.rectangle((5, 21 + bob, 9, 25 + bob), fill=BLUE)
    else:
        y = 21 + bob
        draw.rectangle((4, y, 8, y + 4), fill=BLUE)
        draw.rectangle((31, y, 35, y + 4), fill=BLUE)
    if step == 0:
        draw.rectangle((10, 30, 16, 35), fill=BLUE)
        draw.rectangle((23, 31, 30, 36), fill=BLUE_D)
    else:
        draw.rectangle((10, 31, 16, 36), fill=BLUE_D)
        draw.rectangle((23, 30, 30, 35), fill=BLUE)
    return image


def draw_side(step: int) -> Image.Image:
    image = blank(40, 40)
    draw = ImageDraw.Draw(image)
    bob = 0 if step == 0 else 1
    draw.ellipse((7, 10 + bob, 30, 32 + bob), fill=OUT)
    draw.ellipse((8, 11 + bob, 29, 31 + bob), fill=WHITE)
    draw.ellipse((16, 18 + bob, 28, 30 + bob), fill=SHADE)
    draw.rectangle((16, 5 + bob, 18, 13 + bob), fill=OUT)
    draw.ellipse((12, 1 + bob, 22, 10 + bob), fill=OUT)
    draw.ellipse((13, 2 + bob, 21, 9 + bob), fill=ANT)
    draw.rectangle((22, 17 + bob, 26, 21 + bob), fill=EYE)
    draw.point((23, 18 + bob), fill=WHITE)
    draw.rectangle((18, 22 + bob, 21, 24 + bob), fill=PINK)
    if step == 0:
        draw.rectangle((26, 20 + bob, 34, 25 + bob), fill=BLUE)
        draw.rectangle((12, 30, 19, 36), fill=BLUE)
        draw.rectangle((22, 31, 29, 36), fill=BLUE_D)
    else:
        draw.rectangle((8, 21 + bob, 14, 25 + bob), fill=BLUE)
        draw.rectangle((14, 31, 21, 36), fill=BLUE_D)
        draw.rectangle((24, 30, 31, 35), fill=BLUE)
    return image


def draw_back(step: int) -> Image.Image:
    image = blank(40, 40)
    draw = ImageDraw.Draw(image)
    bob = 0 if step == 0 else 1
    draw.ellipse((8, 9 + bob, 31, 32 + bob), fill=OUT)
    draw.ellipse((9, 10 + bob, 30, 31 + bob), fill=WHITE)
    draw.pieslice((12, 16 + bob, 27, 30 + bob), 20, 160, fill=SHADE)
    draw.rectangle((19, 4 + bob, 21, 12 + bob), fill=OUT)
    draw.ellipse((15, 1 + bob, 25, 10 + bob), fill=OUT)
    draw.ellipse((16, 2 + bob, 24, 9 + bob), fill=ANT)
    draw.rectangle((5, 20 + bob, 9, 24 + bob), fill=BLUE)
    draw.rectangle((30, 20 + bob, 34, 24 + bob), fill=BLUE)
    if step == 0:
        draw.rectangle((11, 30, 17, 36), fill=BLUE_D)
        draw.rectangle((23, 31, 30, 36), fill=BLUE)
    else:
        draw.rectangle((11, 31, 17, 36), fill=BLUE)
        draw.rectangle((23, 30, 30, 35), fill=BLUE_D)
    return image


def draw_dead(step: int) -> Image.Image:
    image = blank(44, 36)
    draw = ImageDraw.Draw(image)
    draw.ellipse((2, 10, 34, 30), fill=OUT)
    draw.ellipse((3, 11, 33, 29), fill=WHITE)
    draw.line((10, 16, 15, 21), fill=EYE, width=1)
    draw.line((15, 16, 10, 21), fill=EYE, width=1)
    draw.line((20, 16, 25, 21), fill=EYE, width=1)
    draw.line((25, 16, 20, 21), fill=EYE, width=1)
    draw.rectangle((16, 24, 22, 26), fill=PINK_D)
    draw.rectangle((30, 18, 36, 23), fill=BLUE)
    draw.rectangle((24, 26, 30, 31), fill=BLUE_D)
    sx = 34 if step == 0 else 38
    sy = 4 if step == 0 else 2
    draw.rectangle((sx, sy + 2, sx + 1, sy + 6), fill=ANT)
    draw.rectangle((sx - 2, sy + 3, sx + 3, sy + 4), fill=ANT)
    return image


def draw_bomb(step: int) -> Image.Image:
    image = blank(18, 22)
    draw = ImageDraw.Draw(image)
    draw.rectangle((8, 2, 9, 7), fill=OUT)
    spark = YELLOW if step == 0 else CREAM
    draw.ellipse((6, 0, 11, 5), fill=spark)
    draw.ellipse((2, 6, 15, 20), fill=OUT)
    draw.ellipse((3, 7, 14, 19), fill=BLACK)
    draw.point((6, 10), fill=WHITE)
    draw.point((7, 10), fill=WHITE)
    draw.point((6, 11), fill=(180, 180, 190, 255))
    return image


def draw_boom(step: int) -> Image.Image:
    image = blank(48, 48)
    draw = ImageDraw.Draw(image)
    reach = 8 + step * 4
    arm = (CREAM, YELLOW, ORANGE, RED)[step]
    core = (YELLOW, ORANGE, RED, DARKRED)[step]
    cx = cy = 24
    draw.rectangle((cx - 3, cy - reach, cx + 3, cy + reach), fill=OUT)
    draw.rectangle((cx - reach, cy - 3, cx + reach, cy + 3), fill=OUT)
    draw.rectangle((cx - 2, cy - reach + 1, cx + 2, cy + reach - 1), fill=arm)
    draw.rectangle((cx - reach + 1, cy - 2, cx + reach - 1, cy + 2), fill=arm)
    draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=OUT)
    draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=core)
    draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=CREAM if step < 2 else YELLOW)
    return image


def draw_item(kind: str) -> Image.Image:
    image = blank(16, 16)
    draw = ImageDraw.Draw(image)
    if kind == "fire":
        draw.polygon([(8, 1), (13, 8), (11, 8), (14, 15), (2, 15), (5, 8), (3, 8)], fill=RED)
        draw.polygon([(8, 5), (11, 10), (8, 14), (5, 10)], fill=YELLOW)
    elif kind == "extra":
        draw.ellipse((2, 4, 13, 15), fill=BLACK)
        draw.point((5, 7), fill=WHITE)
        draw.rectangle((7, 1, 8, 5), fill=YELLOW)
    elif kind == "skate":
        draw.polygon([(3, 8), (12, 6), (14, 9), (11, 11), (4, 12)], fill=BLUE)
        draw.rectangle((4, 12, 13, 14), fill=OUT)
        draw.rectangle((5, 12, 7, 14), fill=WHITE)
        draw.rectangle((10, 12, 12, 14), fill=WHITE)
    else:
        draw.polygon([(8, 14), (2, 7), (3, 3), (8, 6), (13, 3), (14, 7)], fill=PINK)
        draw.point((6, 6), fill=ANT_L)
    return image


FONT = {
    "H": ["#.#", "###", "#.#", "#.#", "#.#"],
    "O": [".#.", "#.#", "#.#", "#.#", ".#."],
    "L": ["#..", "#..", "#..", "#..", "###"],
    "A": [".#.", "#.#", "###", "#.#", "#.#"],
    "G": [".#.", "#.#", "#..", "#.#", ".#."],
    "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "!": ["#", "#", "#", ".", "#"],
    "U": ["#.#", "#.#", "#.#", "#.#", ".#."],
    "Y": ["#.#", "#.#", ".#.", ".#.", ".#."],
    "P": ["##.", "#.#", "##.", "#..", "#.."],
}


def bubble(word: str, fill: tuple[int, int, int, int]) -> Image.Image:
    width = 0
    for char in word:
        glyph = FONT[char]
        width += len(glyph[0]) + 1
    image = blank(width + 5, 11)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width + 4, 8), fill=(255, 255, 255, 255))
    draw.rectangle((0, 0, width + 4, 8), outline=OUT)
    draw.rectangle((width // 2, 8, width // 2 + 2, 10), fill=(255, 255, 255, 255))
    x = 2
    pixels = image.load()
    for char in word:
        glyph = FONT[char]
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "#":
                    pixels[x + gx, 2 + gy] = fill
        x += len(glyph[0]) + 1
    return image


def flood_clear(image: Image.Image, colors: set[tuple[int, int, int]]) -> Image.Image:
    image = image.copy()
    pixels = image.load()
    width, height = image.size
    seen = bytearray(width * height)
    stack = [(x, 0) for x in range(width)]
    stack += [(x, height - 1) for x in range(width)]
    stack += [(0, y) for y in range(height)]
    stack += [(width - 1, y) for y in range(height)]
    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= width or y >= height:
            continue
        index = y * width + x
        if seen[index]:
            continue
        seen[index] = 1
        red, green, blue, alpha = pixels[x, y]
        if alpha == 0 or (red, green, blue) in colors:
            pixels[x, y] = (0, 0, 0, 0)
            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))
    return image


def strip_shadow(image: Image.Image) -> Image.Image:
    # La sombra del sprite es un ovalo negro suelto. El contorno del
    # cuerpo tambien es negro, pero toca el color del traje, asi que se queda.
    image = image.convert("RGBA")
    pixels = image.load()
    width, height = image.size
    drop: list[tuple[int, int]] = []
    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            if alpha < 20 or (red, green, blue) != (0, 0, 0):
                continue
            ink = False
            for ny in range(max(0, y - 1), min(height, y + 2)):
                for nx in range(max(0, x - 1), min(width, x + 2)):
                    if nx == x and ny == y:
                        continue
                    pred, pgreen, pblue, palpha = pixels[nx, ny]
                    if palpha > 20 and (pred, pgreen, pblue) != (0, 0, 0):
                        ink = True
                        break
                if ink:
                    break
            if not ink:
                drop.append((x, y))
    for x, y in drop:
        pixels[x, y] = (0, 0, 0, 0)
    return image


def opaque_count(image: Image.Image) -> int:
    pixels = image.load()
    width, height = image.size
    count = 0
    for y in range(height):
        for x in range(width):
            if pixels[x, y][3] > 20:
                count += 1
    return count


def sheet_cell(sheet: Image.Image, col: int, row: int, size: int, gap: int = 0) -> Image.Image:
    x = col * (size + gap)
    y = row * (size + gap)
    return sheet.crop((x, y, x + size, y + size))


def build_frames() -> dict[str, Image.Image]:
    char = Image.open(ART / "bomberman.png").convert("RGBA")
    bombs = Image.open(ART / "bombs.png").convert("RGBA")
    items = Image.open(ART / "items.png").convert("RGBA")
    page = {(112, 146, 190)}
    frame = {(248, 40, 0)}
    green = {(48, 160, 88)}
    sky = {(80, 184, 240)}

    def hero(col: int, row: int) -> Image.Image:
        return scale(strip_shadow(sheet_cell(char, col, row, 32)))

    def bomb(col: int, row: int) -> Image.Image:
        return scale(flood_clear(sheet_cell(bombs, col, row, 16, gap=1), page))

    def powerup(col: int, row: int, mat: set[tuple[int, int, int]]) -> Image.Image:
        cell = sheet_cell(items, col, row, 16)
        return scale(flood_clear(flood_clear(cell, frame), mat))

    frames: dict[str, Image.Image] = {}
    for index, col in enumerate((0, 1, 2)):
        frames[f"front{index}"] = hero(col, 2)
        frames[f"back{index}"] = hero(col, 0)
        frames[f"right{index}"] = hero(col, 1)
        frames[f"left{index}"] = hero(col, 3)
    frames["blink"] = frames["front0"]
    frames["wave0"] = hero(1, 11)
    frames["wave1"] = hero(2, 11)
    frames["mad0"] = hero(1, 7)
    frames["mad1"] = hero(0, 7)
    frames["dead0"] = hero(2, 7)
    frames["dead1"] = hero(3, 7)
    frames["bomb0"] = bomb(0, 0)
    frames["bomb1"] = bomb(1, 0)
    for index, col in enumerate((0, 2, 4, 6)):
        frames[f"boom{index}"] = bomb(col, 1)
    frames["fire"] = powerup(1, 0, green)
    frames["extra"] = powerup(5, 0, sky)
    frames["skate"] = powerup(3, 1, green)
    frames["heart"] = powerup(0, 2, green)
    frames["hola"] = scale(bubble("HOLA", PINK_D))
    frames["grr"] = scale(bubble("GRR", RED))
    frames["hurry"] = scale(bubble("HURRY", ORANGE))
    frames["yay"] = scale(bubble("YAY", ANT))
    frames["up"] = scale(bubble("UP", BLUE))
    for row in range(18):
        for col in range(4):
            if (col, row) == (0, 13):
                continue
            raw = sheet_cell(char, col, row, 32)
            if opaque_count(raw) < 40:
                continue
            frames[f"p{col}_{row}"] = scale(strip_shadow(raw))
    frames["p2_18"] = scale(strip_shadow(sheet_cell(char, 2, 18, 32)))
    return frames


# Caminar, saludar, festejar, una patada, sentarse y ganar.
# Las vueltas y el segundo puntapie se veian sueltos, sin motivo.
CLIPS: dict[str, list[str]] = {
    "front": ["p0_2", "p1_2", "p2_2"],
    "back": ["p0_0", "p1_0", "p2_0"],
    "right": ["p0_1", "p1_1", "p2_1"],
    "left": ["p0_3", "p1_3", "p2_3"],
    "cheer": ["p0_11", "p1_11", "p2_11"],
    "wave": ["p1_13", "p2_13", "p3_13"],
    "kick": ["p0_6", "p1_6", "p2_6", "p3_6"],
    "angry": ["p1_7", "p0_7"],
    "dead": ["p2_7", "p3_7"],
    "sit": ["p0_14", "p1_14", "p2_14", "p3_14"],
    "win": ["p0_15", "p1_15", "p2_15"],
}
TRICKS = ["wave", "cheer", "kick", "sit", "win"]


def make_boom() -> None:
    rate = 22050
    count = int(rate * 0.42)
    rng = random.Random(4)
    frames = bytearray()
    for index in range(count):
        t = index / rate
        env = math.exp(-t * 7.5)
        noise = rng.uniform(-1, 1)
        tone = math.sin(2 * math.pi * (70 + 90 * math.exp(-t * 10)) * t)
        click = math.sin(2 * math.pi * 160 * t) * max(0.0, 1 - index / 90)
        sample = (noise * 0.45 + tone * 0.7 + click * 0.35) * env
        sample = max(-1.0, min(1.0, sample))
        frames += struct.pack("<h", int(sample * 22000))
    with wave.open(str(WAV), "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(frames)


def work_area() -> tuple[int, int, int, int]:
    rect = RECT()
    user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)
    if rect.right <= rect.left:
        return 0, 0, 1366, 728
    return rect.left, rect.top, rect.right, rect.bottom


def listview_hwnd() -> int:
    def from_parent(parent: int) -> int:
        shell = user32.FindWindowExW(parent, None, "SHELLDLL_DefView", None)
        if not shell:
            return 0
        return user32.FindWindowExW(shell, None, "SysListView32", "FolderView") or 0

    progman = user32.FindWindowW("Progman", None)
    found = from_parent(progman)
    if found:
        return found
    hits: list[int] = []

    def visit(hwnd: int, _lparam: int) -> bool:
        name = ctypes.create_unicode_buffer(32)
        user32.GetClassNameW(hwnd, name, 32)
        if name.value == "WorkerW":
            view = from_parent(hwnd)
            if view:
                hits.append(view)
        return True

    user32.EnumWindows(WNDENUMPROC(visit), 0)
    return hits[0] if hits else 0


def icon_points() -> list[tuple[int, int]]:
    view = listview_hwnd()
    if not view:
        return []
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(view, ctypes.byref(pid))
    access = 0x0400 | 0x0008 | 0x0010 | 0x0020
    process = kernel32.OpenProcess(access, False, pid.value)
    if not process:
        return []
    points: list[tuple[int, int]] = []
    try:
        count_slot = ctypes.c_size_t(0)
        user32.SendMessageTimeoutW(view, 0x1004, 0, None, 0x0002, 250, ctypes.byref(count_slot))
        count = int(count_slot.value)
        origin = POINT(0, 0)
        user32.ClientToScreen(view, ctypes.byref(origin))
        for index in range(min(count, 48)):
            remote = kernel32.VirtualAllocEx(process, None, ctypes.sizeof(POINT), 0x1000, 0x04)
            if not remote:
                break
            try:
                done = ctypes.c_size_t(0)
                user32.SendMessageTimeoutW(
                    view, 0x1010, index, remote, 0x0002, 250, ctypes.byref(done),
                )
                local = POINT()
                kernel32.ReadProcessMemory(
                    process, remote, ctypes.byref(local), ctypes.sizeof(POINT), None,
                )
                points.append((origin.x + local.x + 32, origin.y + local.y + 18))
            finally:
                kernel32.VirtualFreeEx(process, remote, 0, 0x8000)
    finally:
        kernel32.CloseHandle(process)
    return points


def window_rects(skip: int) -> list[tuple[int, int, int, int]]:
    rects: list[tuple[int, int, int, int]] = []
    dwm = None
    try:
        dwm = ctypes.WinDLL("dwmapi")
        dwm.DwmGetWindowAttribute.argtypes = [
            wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD,
        ]
        dwm.DwmGetWindowAttribute.restype = ctypes.c_long
    except OSError:
        dwm = None

    def visit(hwnd: int, _lparam: int) -> bool:
        if hwnd == skip or not user32.IsWindowVisible(hwnd):
            return True
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        if style & WS_EX_TOOLWINDOW:
            return True
        if dwm is not None:
            cloaked = ctypes.c_int(0)
            try:
                dwm.DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, ctypes.byref(cloaked), 4)
            except OSError:
                cloaked.value = 0
            if cloaked.value:
                return True
        rect = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        if width < 120 or height < 90:
            return True
        name = ctypes.create_unicode_buffer(48)
        user32.GetClassNameW(hwnd, name, 48)
        if name.value in {"Progman", "WorkerW", "Shell_TrayWnd", "Shell_SecondaryTrayWnd"}:
            return True
        rects.append((rect.left, rect.top, rect.right, rect.bottom))
        return True

    user32.EnumWindows(WNDENUMPROC(visit), 0)
    return rects


def covered(rects: list[tuple[int, int, int, int]], x: int, y: int) -> bool:
    for left, top, right, bottom in rects:
        if left <= x < right and top <= y < bottom:
            return True
    return False


def find_grok() -> int:
    found: list[int] = []

    def visit(hwnd: int, _lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        name = ctypes.create_unicode_buffer(64)
        user32.GetClassNameW(hwnd, name, 64)
        if "Chrome" in name.value or "Mozilla" in name.value:
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        title = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, title, length + 1)
        text = title.value.lower().strip()
        if text.endswith("grok"):
            found.append(hwnd)
        return True

    user32.EnumWindows(WNDENUMPROC(visit), 0)
    return found[0] if found else 0


def foreground(hwnd: int) -> None:
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)
    current = user32.GetForegroundWindow()
    current_thread = user32.GetWindowThreadProcessId(current, None)
    target_thread = user32.GetWindowThreadProcessId(hwnd, None)
    this_thread = kernel32.GetCurrentThreadId()
    user32.AttachThreadInput(this_thread, current_thread, True)
    user32.AttachThreadInput(this_thread, target_thread, True)
    user32.SetForegroundWindow(hwnd)
    user32.AttachThreadInput(this_thread, current_thread, False)
    user32.AttachThreadInput(this_thread, target_thread, False)


def wake_grok() -> None:
    hwnd = find_grok()
    if hwnd:
        foreground(hwnd)
        log("grok al frente")
        return
    if not GROK.exists():
        log("no esta grok.exe")
        return
    subprocess.Popen(
        [str(GROK)],
        cwd=str(Path.home()),
        creationflags=0x00000010 | 0x00000200,
        close_fds=True,
    )
    log("grok encendido")


_quiet_until = 0.0


def play_wav(path: Path, hold: float = 0.0) -> None:
    global _quiet_until
    if not path.exists():
        return
    if hold:
        _quiet_until = time.time() + hold
    try:
        winsound.PlaySound(
            str(path),
            winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
        )
    except (RuntimeError, OSError) as exc:
        log(f"sonido {exc}")


# El archivo de los pasos queda igual que en Descargas.
# Al reproducir se baja el nivel para que no taladre. Las otras voces no cambian.
WAVE_MAPPER = 0xFFFFFFFF
WHDR_DONE = 0x00000001
STEP_GAIN = 0.38


class WAVEFORMATEX(ctypes.Structure):
    _fields_ = [
        ("wFormatTag", wintypes.WORD),
        ("nChannels", wintypes.WORD),
        ("nSamplesPerSec", wintypes.DWORD),
        ("nAvgBytesPerSec", wintypes.DWORD),
        ("nBlockAlign", wintypes.WORD),
        ("wBitsPerSample", wintypes.WORD),
        ("cbSize", wintypes.WORD),
    ]


class WAVEHDR(ctypes.Structure):
    _fields_ = [
        ("lpData", ctypes.c_void_p),
        ("dwBufferLength", wintypes.DWORD),
        ("dwBytesRecorded", wintypes.DWORD),
        ("dwUser", ctypes.c_ulonglong),
        ("dwFlags", wintypes.DWORD),
        ("dwLoops", wintypes.DWORD),
        ("lpNext", ctypes.c_void_p),
        ("reserved", ctypes.c_void_p),
    ]


winmm.waveOutOpen.argtypes = [
    ctypes.POINTER(wintypes.HANDLE), ctypes.c_uint,
    ctypes.POINTER(WAVEFORMATEX), ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD,
]
winmm.waveOutOpen.restype = wintypes.UINT
winmm.waveOutPrepareHeader.argtypes = [wintypes.HANDLE, ctypes.POINTER(WAVEHDR), wintypes.UINT]
winmm.waveOutPrepareHeader.restype = wintypes.UINT
winmm.waveOutWrite.argtypes = [wintypes.HANDLE, ctypes.POINTER(WAVEHDR), wintypes.UINT]
winmm.waveOutWrite.restype = wintypes.UINT
winmm.waveOutReset.argtypes = [wintypes.HANDLE]
winmm.waveOutReset.restype = wintypes.UINT


class StepVoice:
    def __init__(self) -> None:
        self.out: dict[str, int] = {}
        self.hdr: dict[str, WAVEHDR] = {}
        self.buf: dict[str, ctypes.Array] = {}

    def load(self, name: str, path: Path) -> int:
        if not path.exists():
            return 1
        src = wave.open(str(path))
        try:
            channels = src.getnchannels()
            rate = src.getframerate()
            width = src.getsampwidth()
            pcm = src.readframes(src.getnframes())
        finally:
            src.close()
        fmt = WAVEFORMATEX()
        fmt.wFormatTag = 1
        fmt.nChannels = channels
        fmt.nSamplesPerSec = rate
        fmt.wBitsPerSample = width * 8
        fmt.nBlockAlign = channels * width
        fmt.nAvgBytesPerSec = rate * fmt.nBlockAlign
        fmt.cbSize = 0
        samples = struct.unpack("<" + "h" * (len(pcm) // 2), pcm)
        quiet = struct.pack(
            "<" + "h" * len(samples),
            *[max(-32767, min(32767, int(s * STEP_GAIN))) for s in samples],
        )
        buf = ctypes.create_string_buffer(quiet)
        opened = wintypes.HANDLE()
        err = winmm.waveOutOpen(
            ctypes.byref(opened), WAVE_MAPPER, ctypes.byref(fmt), None, None, 0,
        )
        if err:
            return err
        hdr = WAVEHDR()
        hdr.lpData = ctypes.cast(buf, ctypes.c_void_p)
        hdr.dwBufferLength = len(quiet)
        err = winmm.waveOutPrepareHeader(opened, ctypes.byref(hdr), ctypes.sizeof(hdr))
        if err:
            return err
        self.buf[name] = buf
        self.hdr[name] = hdr
        self.out[name] = int(opened.value or 0)
        return 0

    def play(self, name: str) -> None:
        handle = self.out.get(name)
        hdr = self.hdr.get(name)
        if not handle or hdr is None:
            return
        winmm.waveOutReset(handle)
        hdr.dwFlags &= ~WHDR_DONE
        winmm.waveOutWrite(handle, ctypes.byref(hdr), ctypes.sizeof(hdr))


steps = StepVoice()


def open_steps() -> None:
    for name, path in (("h", STEP_H), ("v", STEP_V)):
        err = steps.load(name, path)
        if err:
            log(f"paso {name} {err}")


def play_hurry() -> None:
    if not HURRY.exists():
        log("sin hurry.mp3")
        return
    path = str(HURRY).replace("\\", "/")
    winmm.mciSendStringW("close hurry", None, 0, None)
    err = winmm.mciSendStringW(
        f'open "{path}" type mpegvideo alias hurry',
        None,
        0,
        None,
    )
    if err:
        log(f"hurry mci {err}")
        return
    winmm.mciSendStringW("setaudio hurry volume to 800", None, 0, None)
    winmm.mciSendStringW("play hurry", None, 0, None)
    log("hurry up")


class World:
    def __init__(self) -> None:
        self.rng = random.Random()
        left, top, right, bottom = work_area()
        self.bounds = (left + 40, top + 40, right - 40, bottom - 40)
        self.x = float(min(right - 80, left + 180))
        self.y = float((top + bottom) // 2)
        self.vx = float(WALK)
        self.vy = 0.0
        self.state = "greet"
        self.timer = 2.0
        self.step_time = 0.0
        self.blink = 0.0
        self.bomb = None
        self.boom = None
        self.items: list[dict] = []
        self.sparks: list[dict] = []
        self.facing = "right"
        self.invuln = 0.0
        self.next_bomb = 8.0
        self.next_greet = 24.0
        self.grok_cool = 0.0
        self.icons: list[tuple[int, int]] = []
        self.rects: list[tuple[int, int, int, int]] = []
        self.scan_in = 0.0
        self.target = (self.x + 120, self.y)
        self.clumsy = False
        self.flee_for = 0.0
        self.frame_age = 0.0
        self.heart = 0.0
        self.sink_in = 0.0
        self.shake = 0.0
        self.hurry_stamp = None
        self.hurry_left = 0.0
        self.clock_in = 0.0
        self.clip_name = "cheer"
        self.trick_i = 0
        self.hug = False
        self.near = False
        self.grabbed = False
        self.carrying = False
        self.grab_x = 0
        self.grab_y = 0
        self.mx = 0
        self.my = 0
        self.last_click = 0.0
        self.pending_trick = False
        self.trick_at = 0.0
        self.next_show = 9.0
        self.show_age = 0.0
        self.step_i = -1

    def set_facing(self, facing: str, speed: float = WALK) -> None:
        # En la NES solo hay cuatro rumbos. Arriba muestra la espalda.
        self.facing = facing
        if facing == "left":
            self.vx, self.vy = -speed, 0.0
        elif facing == "right":
            self.vx, self.vy = speed, 0.0
        elif facing == "back":
            self.vx, self.vy = 0.0, -speed
        else:
            self.vx, self.vy = 0.0, speed

    def hits_wall(self, facing: str) -> bool:
        left, top, right, bottom = self.bounds
        if facing == "left":
            return self.x <= left + 2
        if facing == "right":
            return self.x >= right - 2
        if facing == "back":
            return self.y <= top + 2
        return self.y >= bottom - 2

    def walk_toward(self, tx: float, ty: float, speed: float = WALK) -> None:
        # Termina el eje en el que ya va y despues gira. No corta en diagonal.
        dx = tx - self.x
        dy = ty - self.y
        ax = abs(dx)
        ay = abs(dy)
        if self.vx != 0 and ax >= 16:
            facing = "right" if dx > 0 else "left"
        elif self.vy != 0 and ay >= 16:
            facing = "front" if dy > 0 else "back"
        elif ax < 16 and ay < 16:
            self.vx = self.vy = 0.0
            return
        elif ax >= ay:
            facing = "right" if dx > 0 else "left"
        else:
            facing = "front" if dy > 0 else "back"
        if self.hits_wall(facing):
            if facing in {"left", "right"} and ay >= 16:
                facing = "front" if dy > 0 else "back"
            elif facing in {"front", "back"} and ax >= 16:
                facing = "right" if dx > 0 else "left"
            if self.hits_wall(facing):
                self.vx = self.vy = 0.0
                return
        self.set_facing(facing, speed)

    def clamp(self) -> None:
        left, top, right, bottom = self.bounds
        speed = max(abs(self.vx), abs(self.vy), WALK)
        if self.x < left:
            self.x = left
            self.set_facing("right", speed)
        elif self.x > right:
            self.x = right
            self.set_facing("left", speed)
        elif self.y < top:
            self.y = top
            self.set_facing("front", speed)
        elif self.y > bottom:
            self.y = bottom
            self.set_facing("back", speed)

    def free_point(self) -> tuple[float, float]:
        left, top, right, bottom = self.bounds
        free = []
        y = top
        while y < bottom:
            x = left
            while x < right:
                if not covered(self.rects, int(x), int(y)):
                    free.append((x, y))
                x += 110
            y += 100
        if free:
            return self.rng.choice(free)
        return (
            self.rng.uniform(left, right),
            self.rng.uniform(top, bottom),
        )

    def scan(self) -> None:
        self.icons = icon_points()
        front = user32.GetForegroundWindow()
        if front:
            rect = RECT()
            user32.GetWindowRect(front, ctypes.byref(rect))
            self.rects = [(rect.left, rect.top, rect.right, rect.bottom)]
        else:
            self.rects = []

    def plant(self) -> None:
        self.bomb = {"x": self.x, "y": self.y + 8, "t": 1.65}
        self.clumsy = self.rng.random() < 0.30
        if self.clumsy and self.rng.random() < 0.5:
            self.target = (self.x, self.y)
            self.flee_for = 0.0
        else:
            self.target = self.straight_away(240)
            self.flee_for = 0.55 if self.clumsy else 9.0
        self.state = "flee"
        self.timer = 2.2
        play_wav(PLACE, 0.25)
        log("bomba" + (" torpe" if self.clumsy else ""))

    def explode(self) -> None:
        bomb = self.bomb
        self.bomb = None
        if not bomb:
            return
        self.boom = {"x": bomb["x"], "y": bomb["y"], "t": 0.0}
        kind = self.rng.choice(["fire", "extra", "skate", "heart"])
        self.items.append({
            "x": bomb["x"], "y": bomb["y"], "vy": -90.0, "kind": kind, "age": 0.0,
        })
        for _ in range(10):
            ang = self.rng.random() * math.tau
            spd = self.rng.uniform(40, 140)
            self.sparks.append({
                "x": bomb["x"], "y": bomb["y"],
                "vx": math.cos(ang) * spd, "vy": math.sin(ang) * spd - 30,
                "age": 0.0,
                "color": self.rng.choice([ORANGE, YELLOW, CREAM, RED]),
            })
        if math.hypot(self.x - bomb["x"], self.y - bomb["y"]) < 78 and self.invuln <= 0 and self.state not in {"dead", "carry"}:
            self.die()

    def die(self) -> None:
        self.state = "dead"
        self.timer = 2.7
        self.vx = 0
        self.vy = 0
        self.invuln = 3.4
        play_wav(EXPLODE, 1.9)
        log("se mato")

    def respawn(self) -> None:
        self.x, self.y = self.free_point()
        self.state = "greet"
        self.timer = 1.6
        self.facing = "front"

    def poke(self) -> None:
        if self.grok_cool <= 0:
            self.grok_cool = 8.0
            try:
                wake_grok()
            except OSError as exc:
                log(f"grok {exc}")
        if self.state != "dead":
            self.state = "mad"
            self.timer = 1.15
            self.vx = 0
            self.vy = 0
            self.facing = "front"
            self.hug = False
            play_wav(GRITO, 0.6)

    def play_trick(self) -> None:
        if self.state == "dead" or self.carrying:
            return
        self.clip_name = TRICKS[self.trick_i % len(TRICKS)]
        self.trick_i += 1
        self.state = "trick"
        self.timer = 1.25
        self.vx = 0
        self.vy = 0
        self.hug = False

    def straight_away(self, dist: float) -> tuple[float, float]:
        left, top, right, bottom = self.bounds
        options = []
        if self.x - left > 100:
            options.append("left")
        if right - self.x > 100:
            options.append("right")
        if self.y - top > 100:
            options.append("back")
        if bottom - self.y > 100:
            options.append("front")
        facing = self.rng.choice(options or ["left", "right", "front", "back"])
        if facing == "left":
            return self.x - dist, self.y
        if facing == "right":
            return self.x + dist, self.y
        if facing == "back":
            return self.x, self.y - dist
        return self.x, self.y + dist

    def end_grab(self) -> None:
        carried = self.carrying
        self.grabbed = False
        self.carrying = False
        if carried:
            self.pending_trick = False
            self.clip_name = "win"
            self.state = "trick"
            self.timer = 0.9
            play_wav(CAIGO, 0.95)
            return
        now = time.time()
        gap = user32.GetDoubleClickTime() / 1000
        if self.last_click and now - self.last_click <= gap:
            self.last_click = 0.0
            self.pending_trick = False
            self.poke()
        else:
            self.last_click = now
            self.pending_trick = True
            self.trick_at = now + gap

    def read_pointer(self) -> None:
        point = POINT()
        user32.GetCursorPos(ctypes.byref(point))
        self.mx, self.my = point.x, point.y
        down = bool(user32.GetAsyncKeyState(1) & 0x8000)
        if self.grabbed and not down:
            self.end_grab()
        if self.grabbed and down and self.state != "dead":
            moved = math.hypot(self.mx - self.grab_x, self.my - self.grab_y)
            if moved > 12:
                self.carrying = True
            if self.carrying:
                self.x = float(self.mx)
                self.y = float(self.my - 30)
                self.vx = 0
                self.vy = 0
                self.state = "carry"
                self.pending_trick = False
        self.near = math.hypot(self.mx - self.x, self.my - self.y) < 110
        if (
            self.near
            and not self.grabbed
            and self.state not in {"dead", "trick", "mad", "greet", "carry"}
        ):
            if self.state != "chase":
                self.show_age = 0.0
            self.state = "chase"
        if self.pending_trick and time.time() >= self.trick_at and not self.grabbed:
            self.pending_trick = False
            self.play_trick()

    def maybe_hurry(self) -> None:
        now = time.localtime()
        if now.tm_min != 50:
            return
        stamp = (now.tm_yday, now.tm_hour)
        if stamp == self.hurry_stamp:
            return
        self.hurry_stamp = stamp
        self.hurry_left = 2.6
        try:
            play_hurry()
        except OSError as exc:
            log(f"hurry {exc}")

    def update(self, dt: float) -> None:
        self.step_time += dt
        self.blink -= dt
        self.invuln = max(0.0, self.invuln - dt)
        self.grok_cool = max(0.0, self.grok_cool - dt)
        self.scan_in -= dt
        self.frame_age += dt
        self.hurry_left = max(0.0, self.hurry_left - dt)
        self.clock_in -= dt
        if self.clock_in <= 0:
            self.clock_in = 1.0
            self.maybe_hurry()
        if self.scan_in <= 0:
            self.scan_in = 2.5
            try:
                self.scan()
                if not getattr(self, "_scanned", False):
                    self._scanned = True
                    self.x, self.y = self.free_point()
                    box = self.rects[0] if self.rects else None
                    log(f"zona iconos={len(self.icons)} libre={int(self.x)},{int(self.y)} tapa={box}")
            except Exception as exc:
                log(f"scan {exc}")
        if STOP.exists():
            raise SystemExit
        self.read_pointer()

        if self.bomb:
            self.bomb["t"] -= dt
            if self.bomb["t"] <= 0:
                self.explode()
        if self.boom:
            self.boom["t"] += dt
            if self.boom["t"] > 0.48:
                self.boom = None
        alive = []
        for spark in self.sparks:
            spark["age"] += dt
            spark["x"] += spark["vx"] * dt
            spark["y"] += spark["vy"] * dt
            spark["vy"] += 80 * dt
            if spark["age"] < 0.45:
                alive.append(spark)
        self.sparks = alive
        kept = []
        for item in self.items:
            item["age"] += dt
            item["vy"] += 160 * dt
            item["y"] += item["vy"] * dt
            if item["vy"] > 0 and item["y"] > item.get("ground", item["y"]):
                if "ground" not in item:
                    item["ground"] = item["y"]
                item["y"] = item["ground"]
                item["vy"] = 0
            if item["age"] > 0.35 and "ground" not in item:
                item["ground"] = item["y"]
            if self.state != "dead" and math.hypot(item["x"] - self.x, item["y"] - self.y) < 36:
                continue
            if item["age"] < 12:
                kept.append(item)
        self.items = kept

        if self.state == "carry":
            self.facing = "front"
        elif self.state == "trick":
            self.vx = self.vy = 0
            self.timer -= dt
            if self.timer <= 0:
                self.state = "wander"
                self.timer = 1.2
                self.wander_push()
        elif self.state == "chase":
            dist = math.hypot(self.mx - self.x, self.my - self.y)
            if not self.near:
                self.hug = False
                self.state = "wander"
                self.timer = 1.0
                self.wander_push()
            elif dist < 46:
                if not self.hug:
                    self.clip_name = "wave"
                    self.show_age = 0.0
                self.hug = True
                self.vx = self.vy = 0
                self.show_age += dt
                if self.show_age > 2.6:
                    self.show_age = 0.0
                    self.clip_name = "cheer" if self.clip_name == "wave" else "wave"
            else:
                self.hug = False
                self.walk_toward(self.mx, self.my)
                self.move(dt)
        elif self.state == "greet":
            self.facing = "front"
            self.vx = self.vy = 0
            self.timer -= dt
            if self.timer <= 0:
                self.state = "wander"
                self.timer = self.rng.uniform(2.2, 4.2)
                self.wander_push()
        elif self.state == "mad":
            self.facing = "front"
            self.shake += dt
            self.timer -= dt
            if self.timer <= 0:
                self.state = "wander"
                self.timer = 2.0
                self.wander_push()
        elif self.state == "dead":
            self.timer -= dt
            if self.timer <= 0:
                self.respawn()
        elif self.state == "seek":
            self.walk_toward(self.target[0], self.target[1])
            self.move(dt)
            if math.hypot(self.target[0] - self.x, self.target[1] - self.y) < 22:
                self.plant()
        elif self.state == "flee":
            self.timer -= dt
            self.flee_for -= dt
            if self.clumsy and self.flee_for <= 0 and self.bomb:
                self.target = (self.bomb["x"], self.bomb["y"])
            self.walk_toward(self.target[0], self.target[1])
            self.move(dt)
            if not self.bomb and self.boom is None:
                self.state = "wander"
                self.timer = 1.5
        else:
            self.next_bomb -= dt
            self.next_greet -= dt
            self.timer -= dt
            if self.timer <= 0:
                self.timer = self.rng.uniform(2.0, 4.0)
                self.wander_push()
            self.move(dt)
            self.next_show -= dt
            if self.next_show <= 0 and not self.bomb and not self.near:
                self.next_show = self.rng.uniform(18, 32)
                self.clip_name = self.rng.choice(("wave", "cheer", "sit"))
                self.state = "trick"
                self.timer = 1.6
                self.vx = 0
                self.vy = 0
                self.hug = False
            elif self.next_greet <= 0 and not self.bomb:
                self.next_greet = self.rng.uniform(28, 46)
                self.state = "greet"
                self.timer = 1.7
            elif self.next_bomb <= 0 and not self.bomb and not self.boom:
                self.next_bomb = self.rng.uniform(16, 26)
                self.choose_bomb_target()

    def wander_push(self) -> None:
        left, top, right, bottom = self.bounds
        open_ways = []
        if self.x - left > 70:
            open_ways.append("left")
        if right - self.x > 70:
            open_ways.append("right")
        if self.y - top > 70:
            open_ways.append("back")
        if bottom - self.y > 70:
            open_ways.append("front")
        if not open_ways:
            open_ways = ["left", "right", "front", "back"]
        opposite = {"left": "right", "right": "left", "front": "back", "back": "front"}
        sideways = [way for way in open_ways if way != self.facing and way != opposite.get(self.facing)]
        roll = self.rng.random()
        if roll < 0.6 and sideways:
            facing = self.rng.choice(sideways)
        elif self.facing in open_ways and roll < 0.85:
            facing = self.facing
        else:
            back = opposite.get(self.facing, "right")
            facing = back if back in open_ways else self.rng.choice(open_ways)
        self.set_facing(facing)

    def choose_bomb_target(self) -> None:
        free_icons = [p for p in self.icons if not covered(self.rects, p[0], p[1])]
        if free_icons and self.rng.random() < 0.75:
            self.target = self.rng.choice(free_icons)
        else:
            self.target = self.free_point()
        self.state = "seek"

    def move(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.clamp()
        self.footstep()

    def footstep(self) -> None:
        # Tres cuadros de caminata: el del medio es el paso en el aire.
        # Suena al apoyar, izquierda y derecha, o arriba y abajo.
        speed = math.hypot(self.vx, self.vy)
        # Pie, junto, pie, junto. El pack cae parejo, no dos seguidos.
        phase = int(self.step_time * 8) % 4
        if speed < 18 or phase == self.step_i or phase in {1, 3}:
            self.step_i = phase
            return
        self.step_i = phase
        if time.time() < _quiet_until or self.hurry_left > 0:
            return
        steps.play("v" if abs(self.vy) > abs(self.vx) else "h")

    def hero_key(self) -> str:
        if self.state == "dead":
            name = "dead"
        elif self.state == "mad":
            name = "angry"
        elif self.state == "carry":
            return CLIPS["cheer"][1]
        elif self.state == "greet":
            name = "wave"
        elif self.state == "trick" or (self.state == "chase" and self.hug):
            name = self.clip_name
        else:
            name = self.facing
        seq = CLIPS.get(name) or CLIPS["front"]
        if name in {"front", "back", "left", "right"}:
            if math.hypot(self.vx, self.vy) < 18:
                return seq[1]
            phase = int(self.step_time * 8) % 4
            return seq[(0, 1, 2, 1)[phase]]
        return seq[int(self.step_time * 8) % len(seq)]


def paste(frame: Image.Image, sprite: Image.Image, cx: int, cy: int, origin: tuple[int, int]) -> None:
    x = int(cx - origin[0] - sprite.width / 2)
    y = int(cy - origin[1] - sprite.height / 2)
    frame.paste(sprite, (x, y), sprite)


def render(world: World, frames: dict[str, Image.Image]) -> Image.Image:
    sprites: list[tuple[Image.Image, float, float]] = []
    hx = world.x + (math.sin(world.shake * 40) * 3 if world.state == "mad" else 0)
    hy = world.y
    sprites.append((frames[world.hero_key()], hx, hy))
    lift = hy - 72
    if world.state == "greet":
        sprites.append((frames["hola"], hx, lift))
    elif world.state == "mad":
        sprites.append((frames["grr"], hx, lift))
    elif world.state == "carry":
        sprites.append((frames["up"], hx, lift))
    elif world.state == "trick" and world.clip_name in {"cheer", "win", "wave"}:
        bubble_key = "hola" if world.clip_name == "wave" else "yay"
        sprites.append((frames[bubble_key], hx, lift))
    elif world.hurry_left > 0:
        sprites.append((frames["hurry"], hx, lift))
    # Al sujetarlo la ventana es solo el y su globo. Meter la bomba
    # en el mismo recorte cambia el tamano en cada pixel y parpadea.
    held = world.state == "carry"
    if not held and world.bomb:
        key = "bomb1" if int(world.bomb["t"] * 8) % 2 else "bomb0"
        sprites.append((frames[key], world.bomb["x"], world.bomb["y"]))
    if not held and world.boom:
        step = min(3, int(world.boom["t"] * 8))
        sprites.append((frames[f"boom{step}"], world.boom["x"], world.boom["y"]))
    if not held:
        for item in world.items:
            hop = math.sin(item["age"] * 6) * 2
            sprites.append((frames[item["kind"]], item["x"], item["y"] + hop))
    if not sprites and not world.sparks:
        sprites.append((frames["front0"], world.x, world.y))
    boxes = []
    for sprite, cx, cy in sprites:
        boxes.append((cx - sprite.width / 2, cy - sprite.height / 2, cx + sprite.width / 2, cy + sprite.height / 2))
    if not held:
        for spark in world.sparks:
            boxes.append((spark["x"] - 2, spark["y"] - 2, spark["x"] + 2, spark["y"] + 2))
    minx = int(min(b[0] for b in boxes)) - 2
    miny = int(min(b[1] for b in boxes)) - 2
    maxx = int(max(b[2] for b in boxes)) + 2
    maxy = int(max(b[3] for b in boxes)) + 2
    frame = Image.new("RGB", (max(1, maxx - minx), max(1, maxy - miny)), MAGENTA)
    for sprite, cx, cy in sprites:
        paste(frame, sprite, int(cx), int(cy), (minx, miny))
    if not held and world.sparks:
        draw = ImageDraw.Draw(frame)
        for spark in world.sparks:
            color = spark["color"][:3]
            x = int(spark["x"] - minx)
            y = int(spark["y"] - miny)
            draw.rectangle((x, y, x + 2, y + 2), fill=color)
    return frame, minx, miny


def save_sheet(frames: dict[str, Image.Image]) -> None:
    order = [
        "front0", "front1", "wave0", "wave1", "mad0", "blink",
        "right0", "right1", "left0", "back0", "dead0", "dead1",
        "bomb0", "bomb1", "boom0", "boom1", "boom2", "boom3",
        "fire", "extra", "skate", "heart", "hola", "grr",
    ]
    pad = 8
    width = sum(frames[name].width + pad for name in order) + pad
    height = max(frames[name].height for name in order) + pad * 2
    sheet = Image.new("RGB", (width, height), (32, 28, 42))
    x = pad
    for name in order:
        sprite = frames[name]
        sheet.paste(sprite, (x, pad), sprite)
        x += sprite.width + pad
    path = HERE / "sheet.png"
    sheet.save(path)
    print(path)


def hwnd_of(root) -> int:
    ident = int(root.winfo_id())
    parent = user32.GetParent(ident)
    return int(parent or ident)


def ensure_style(hwnd: int) -> None:
    style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    want = (style | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE) & ~WS_EX_TRANSPARENT
    if style != want:
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, want)


def apply_icon(hwnd: int) -> None:
    if not ICON.exists():
        return
    big = user32.LoadImageW(None, str(ICON), 1, 32, 32, 0x0010)
    small = user32.LoadImageW(None, str(ICON), 1, 16, 16, 0x0010)
    if big:
        user32.SendMessageW(hwnd, 0x0080, 1, ctypes.c_void_p(int(big)))
    if small:
        user32.SendMessageW(hwnd, 0x0080, 0, ctypes.c_void_p(int(small)))


def sink(hwnd: int, x: int, y: int, w: int, h: int) -> None:
    # Encima, pero sin robar el foco. Chrome a pantalla completa tapa
    # cualquier ventana que de verdad quede debajo, y entonces no se ve
    # ni se puede hacer clic.
    user32.SetWindowPos(
        hwnd, -1, int(x), int(y), int(w), int(h),
        SWP_NOACTIVATE | SWP_SHOWWINDOW,
    )


def run() -> None:
    import tkinter as tk

    if STOP.exists():
        STOP.unlink()
    LOG.write_text("", encoding="utf-8")
    try:
        stream = open(LOG, "a", encoding="utf-8", buffering=1)
        sys.stdout = stream
        sys.stderr = stream
    except OSError:
        pass
    kernel32.SetPriorityClass(kernel32.GetCurrentProcess(), 0x00004000)
    mutex = kernel32.CreateMutexW(None, False, "Local\\JonnyBomberPet")
    if kernel32.GetLastError() == 183:
        log("ya hay un bomber")
        return
    if not WAV.exists():
        make_boom()
    frames = build_frames()
    world = World()
    root = tk.Tk()
    root.title("pety bombaman")
    try:
        root.iconbitmap(str(ICON))
    except tk.TclError:
        pass
    root.overrideredirect(True)
    root.configure(bg=KEY)
    root.attributes("-transparentcolor", KEY)
    root.attributes("-topmost", False)
    root.withdraw()
    label = tk.Label(root, bg=KEY, bd=0, highlightthickness=0)
    label.pack()
    root.update_idletasks()
    hwnd = hwnd_of(root)
    ensure_style(hwnd)
    user32.SetWindowTextW(hwnd, "pety bombaman")
    apply_icon(hwnd)
    root.deiconify()
    photo_box = {"image": None, "geo": ""}

    def on_left(_event) -> None:
        if world.state == "dead":
            return
        point = POINT()
        user32.GetCursorPos(ctypes.byref(point))
        world.grabbed = True
        world.carrying = False
        world.grab_x = point.x
        world.grab_y = point.y

    def on_right(_event) -> None:
        log("adios")
        root.destroy()

    label.bind("<Button-1>", on_left)
    label.bind("<Button-3>", on_right)
    root.bind("<Button-1>", on_left)
    root.bind("<Button-3>", on_right)

    def tick() -> None:
        try:
            if world.step_time < 12:
                beat(f"update {world.step_time:.1f} {world.state}")
            world.update(FPS_MS / 1000)
            if world.step_time < 12:
                beat("render")
            frame, x, y = render(world, frames)
            if world.step_time < 12:
                beat(f"photo {frame.size}")
            size = (frame.width, frame.height)
            # Misma pose mientras lo arrastras: no se vuelve a pintar.
            # Repintar la ventana con color clave en cada pixel la hace parpadear.
            stamp = ("carry", size) if world.state == "carry" else None
            if stamp is not None and stamp == photo_box.get("stamp"):
                user32.SetWindowPos(
                    hwnd, 0, int(x), int(y), 0, 0,
                    SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE,
                )
            else:
                photo = ImageTk.PhotoImage(frame)
                label.configure(image=photo)
                photo_box["image"] = photo
                photo_box["stamp"] = stamp
                if size != photo_box.get("size"):
                    root.geometry(f"{frame.width}x{frame.height}+{int(x)}+{int(y)}")
                    photo_box["size"] = size
                user32.SetWindowPos(
                    hwnd, -1, int(x), int(y), int(frame.width), int(frame.height),
                    SWP_NOACTIVATE | SWP_SHOWWINDOW,
                )
            if world.step_time - world.heart >= 5:
                world.heart = world.step_time
                log(f"vivo {world.state} {int(world.x)},{int(world.y)}")
            if world.step_time < 12:
                beat(f"ok {world.state} {int(world.x)},{int(world.y)}")
            if world.frame_age >= 8:
                world.frame_age = 0
                frame.save(NOW)
                STATUS.write_text(
                    f"{world.state} {int(world.x)} {int(world.y)}\n",
                    encoding="utf-8",
                )
        except SystemExit:
            root.destroy()
            return
        except Exception:
            log(traceback.format_exc())
        root.after(FPS_MS, tick)

    open_steps()
    log(f"listo hwnd={hwnd}")
    play_wav(LISTO, 0.7)
    def report(exc, val, tb) -> None:
        log("tcl " + "".join(traceback.format_exception(exc, val, tb)))

    root.report_callback_exception = report
    root.after(60, tick)
    root.mainloop()
    log("mainloop termino")
    if mutex:
        kernel32.CloseHandle(mutex)


def main() -> None:
    try:
        fault = open(HERE / "fault.log", "w", encoding="utf-8")
        faulthandler.enable(fault, all_threads=True)
    except OSError:
        pass
    import atexit
    atexit.register(lambda: log("atexit"))
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass
    if "--preview" in sys.argv:
        save_sheet(build_frames())
        return
    try:
        run()
    except Exception:
        log(traceback.format_exc())


if __name__ == "__main__":
    main()
