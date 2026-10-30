#!/bin/sh
# El sistema del vídeo (~/.cache/video-inferencia/sys): el de RTG del vídeo de Trasfondo (3.2, uaegfx 1024x768,
# MUI, AmiSSL, agente) con LightWave, ARexx, Forja, Inferencia y dashc. Sin claves: Inferencia usa Ollama.
#   preparar.sh DASH_DIR MODELO URL
set -e
dash=$1; modelo=$2; url=$3
V=$HOME/.cache/video-inferencia
K=$V/kit                       # LightWave, ARexx y órdenes de C sacados de Coffin (no van al repo)
rm -rf "$V/sys"
cp -r "$HOME/.cache/video-trasfondo/rtgsys" "$V/sys"
rm -f "$V/sys/trasfondo"
/opt/amiga/bin/m68k-amigaos-gcc -noixemul -O2 -o "$V/sys/agente" "$(dirname "$0")/agente.c"
cp "$(dirname "$0")/ScreenMode.prefs" "$V/sys/Prefs/Env-Archive/Sys/"
cp -r "$K/LightWave" "$V/sys/LightWave"
mkdir -p "$V/sys/Rexxc" "$V/sys/System" "$V/sys/Dash" "$V/sys/Hola" "$V/sys/Programas"
cp "$HOME/.cache/dash-emu/sys32rtg8/Libs/rexxsyslib.library" "$V/sys/Libs/"
cp "$K"/x/C/* "$V/sys/C/"; cp "$K"/x/Libs/* "$V/sys/Libs/"; cp "$K"/x/Rexxc/* "$V/sys/Rexxc/"; cp "$K/x/System/RexxMast" "$V/sys/System/"
"$dash/dash" "$HOME/Projects/inferencia/src/main.dash" -o "$V/sys/Programas/Inferencia"
"$dash/dash" "$HOME/Projects/forja/src/main.dash" -o "$V/sys/Programas/Forja"
cp "$dash/dashc/build/dashc.amiga" "$V/sys/Dash/dashc"
cp "$dash"/dashc/build/dashc_*.drt "$V/sys/Dash/"
cp "$(dirname "$0")/ejemplo_mui.dash" "$V/sys/Hola/"
printf '# Hola mundo con MUI\n' > "$V/sys/Hola/hola.dash"
mkdir -p "$V/sys/Encargos"
iconv -f utf-8 -t latin1 "$(dirname "$0")/encargos/letras.txt" > "$V/sys/Encargos/letras.txt"
iconv -f utf-8 -t latin1 "$(dirname "$0")/encargos/hola.txt" > "$V/sys/Encargos/hola.txt"
cat > "$V/sys/S/Startup-Sequence" <<EOS
C:MakeDir RAM:T RAM:ENV RAM:ENV/Sys RAM:Clipboards
C:Assign ENV: RAM:ENV
C:Assign T: RAM:T
C:Assign CLIPS: RAM:Clipboards
C:Assign LOCALE: SYS:Locale
C:Assign KEYMAPS: DEVS:Keymaps
C:Assign LIBS: SYS:Classes ADD
C:AddDataTypes REFRESH QUIET
C:Assign MUI: SYS:MUI
C:Assign LIBS: MUI:Libs ADD
C:Assign LOCALE: MUI:Locale ADD
C:Assign AmiSSL: SYS:AmiSSL
C:Assign LIBS: AmiSSL:Libs ADD
C:SetPatch QUIET
FailAt 21
SYS:Devs/Monitors/uaegfx
C:Copy SYS:Prefs/Env-Archive/Sys/ScreenMode.prefs ENV:Sys/ScreenMode.prefs QUIET
C:Copy SYS:Prefs/Env-Archive/Sys/WBPattern.prefs ENV:Sys/WBPattern.prefs QUIET
C:IPrefs
C:Assign REXX: SYS:Rexxc
Path SYS:Rexxc ADD
SYS:System/RexxMast >NIL:
C:Assign Toaster: SYS:LightWave
C:Assign VT35: SYS:LightWave
C:Assign 3D: SYS:LightWave/3D
C:Assign newtek: SYS:LightWave
C:Assign hiip: SYS:LightWave/Programs/Hiip_Support
C:MakeDir ENV:Forja ENV:Inferencia
C:SetEnv Forja/dashc DH0:Dash/dashc
C:SetEnv Inferencia/proveedor openai
C:SetEnv Inferencia/url $url
C:SetEnv Inferencia/modelo $modelo
C:LoadWB
Run >NIL: DH0:agente
EndCLI >NIL:
EOS
sed -e "s|/home/freemem/.cache/video-trasfondo/rtgsys|$V/sys|g" -e '/DH9:Traspaso/d' "$HOME/.cache/video-trasfondo/rtg.uae" > "$V/video.uae"
grep -n 'DH0\|DH9' "$V/video.uae"
