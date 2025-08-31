#!/usr/bin/env bash
set -euo pipefail

read -rp "Enter version (e.g., 1.2.3): " VERSION
[[ -n "${VERSION}" ]] || { echo "Version is required"; exit 1; }

APP_NAME="Auto Bing Search"
BUNDLE_ID="com.autobingsearch.app"
ROOT="$(pwd)"
ASSETS="$ROOT/assets"

PY312=""
for c in "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3" "/usr/local/bin/python3.12" "$(command -v python3.12)" "$(command -v python3)"; do
  if [ -n "${c:-}" ] && [ -x "$c" ] && "$c" -c 'import sys; print("%d.%d"%sys.version_info[:2])' | grep -qx '3\.12'; then
    PY312="$c"
    break
  fi
done
[ -n "$PY312" ] || { echo "Python 3.12 not found"; exit 1; }

rm -rf dist_arm64 dist_x86_64 dist_universal build_arm64 build_x86_64 spec_arm64 spec_x86_64 .venv_arm .venv_x86

/usr/bin/arch -arm64 "$PY312" -m venv .venv_arm
PIP_NO_COMPILE=1 /usr/bin/arch -arm64 .venv_arm/bin/python -m pip install -U pip wheel setuptools
PIP_NO_COMPILE=1 /usr/bin/arch -arm64 .venv_arm/bin/python -m pip install --no-compile -r requirements.txt pyinstaller pyinstaller-hooks-contrib pyobjc
/usr/bin/arch -arm64 .venv_arm/bin/pyinstaller --clean --noconfirm --windowed \
  --name "$APP_NAME" \
  --icon "$ASSETS/app.icns" \
  --add-data "$ASSETS:assets" \
  --osx-bundle-identifier "$BUNDLE_ID" \
  auto_bing_search.py \
  --distpath dist_arm64 --workpath build_arm64 --specpath spec_arm64

/usr/bin/arch -x86_64 "$PY312" -m venv .venv_x86
PIP_NO_COMPILE=1 /usr/bin/arch -x86_64 .venv_x86/bin/python -m pip install -U pip wheel setuptools
PIP_NO_COMPILE=1 /usr/bin/arch -x86_64 .venv_x86/bin/python -m pip install --no-compile -r requirements.txt pyinstaller pyinstaller-hooks-contrib pyobjc
/usr/bin/arch -x86_64 .venv_x86/bin/pyinstaller --clean --noconfirm --windowed \
  --name "$APP_NAME" \
  --icon "$ASSETS/app.icns" \
  --add-data "$ASSETS:assets" \
  --osx-bundle-identifier "$BUNDLE_ID" \
  auto_bing_search.py \
  --distpath dist_x86_64 --workpath build_x86_64 --specpath spec_x86_64

ARM_APP="$(find dist_arm64 -maxdepth 1 -type d -name "*.app" -print -quit)"
X86_APP="$(find dist_x86_64 -maxdepth 1 -type d -name "*.app" -print -quit)"
[ -d "${ARM_APP:-}" ] && [ -d "${X86_APP:-}" ] || { echo "Missing arch builds"; exit 1; }

mkdir -p dist_universal
cp -R "$ARM_APP" dist_universal/
UNIV_APP="dist_universal/$(basename "$ARM_APP")"

PLIST="$UNIV_APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $VERSION" "$PLIST" 2>/dev/null || /usr/libexec/PlistBuddy -c "Add :CFBundleShortVersionString string $VERSION" "$PLIST"
/usr/libexec/PlistBuddy -c "Set :CFBundleVersion $VERSION" "$PLIST" 2>/dev/null || /usr/libexec/PlistBuddy -c "Add :CFBundleVersion string $VERSION" "$PLIST"

while IFS= read -r -d '' A; do
  REL="${A#"$ARM_APP"/}"
  B="$X86_APP/$REL"
  U="$UNIV_APP/$REL"
  if [ -f "$B" ] && file -b "$A" | grep -q 'Mach-O'; then
    lipo -create "$A" "$B" -output "$U"
  fi
done < <(find "$ARM_APP" -type f -print0)

BIN="$UNIV_APP/Contents/MacOS/$APP_NAME"
[ -f "$BIN" ] || { echo "Universal app binary not found"; exit 1; }

BAD="$(
  find "$UNIV_APP" -type f \( -name "*.dylib" -o -name "*.so" -o -perm -111 \) -print0 \
  | xargs -0 file \
  | grep 'Mach-O' \
  | grep -Ev 'arm64.*x86_64|x86_64.*arm64' || true
)"
if [ -n "$BAD" ]; then
  echo "Non-universal Mach-O detected:"
  echo "$BAD"
  exit 1
fi

find "$UNIV_APP" -name _CodeSignature -type d -exec rm -rf {} + || true
while IFS= read -r -d '' f; do codesign --remove-signature "$f" || true; done < <(find "$UNIV_APP" -type f \( -name "*.dylib" -o -name "*.so" -o -perm -111 \) -print0)

if [ -n "${CODESIGN_IDENTITY:-}" ]; then
  while IFS= read -r -d '' f; do codesign -f -s "$CODESIGN_IDENTITY" --timestamp --options runtime "$f"; done < <(find "$UNIV_APP/Contents/Frameworks" -type f \( -name "*.dylib" -o -name "*.so" -o -perm -111 \) -print0)
  codesign -f -s "$CODESIGN_IDENTITY" --timestamp --options runtime "$UNIV_APP"
else
  while IFS= read -r -d '' f; do codesign -f -s - --timestamp=none "$f"; done < <(find "$UNIV_APP/Contents/Frameworks" -type f \( -name "*.dylib" -o -name "*.so" -o -perm -111 \) -print0)
  codesign -f -s - --timestamp=none "$UNIV_APP"
fi

codesign --verify --deep --strict --verbose=2 "$UNIV_APP" || true
lipo -archs "$BIN"
mdls -name kMDItemExecutableArchitectures "$UNIV_APP" 2>/dev/null || true

if command -v create-dmg >/dev/null 2>&1; then
  DMG="dist_universal/auto-bing-search-universal.dmg"
  rm -f "$DMG"
  create-dmg \
    --volname "$APP_NAME" \
    --volicon "$ASSETS/app.icns" \
    --window-size 540 360 \
    --icon-size 128 \
    --hide-extension "$APP_NAME.app" \
    --icon "$APP_NAME.app" 140 140 \
    --app-drop-link 380 140 \
    --no-internet-enable \
    "$DMG" "$UNIV_APP"
else
  echo "create-dmg not found; skipping DMG packaging"
fi

rm -f Info_extra.plist entitlements.plist

echo "Built: $UNIV_APP"