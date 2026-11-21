#!/bin/bash
# build_mz.sh — сборка Materializr APK (arm64-v8a) в proot Ubuntu
# Режимы: ./build_mz.sh deps  — кросс-сборка SDL3+FreeType+OCCT (~40-80 мин)
#         ./build_mz.sh apk   — только APK (после deps)
#         ./build_mz.sh       — всё по порядку
# Логи шагов: /tmp/mz_deps.log, /tmp/mz_gradle.log
set -e
cd "$(dirname "$0")"
export ANDROID_HOME=/root/android-sdk
export JOBS=4
# CMake 4: старые проекты (OCCT/FreeType) требуют разрешения политики
export CMAKE_POLICY_VERSION_MINIMUM=3.5
NDK=$ANDROID_HOME/ndk/26.3.11579264
BT=$ANDROID_HOME/build-tools/34.0.0

step() { echo; echo "== $1 =="; }

step "0. NDK и правки проекта"
if [ -f $NDK/build/cmake/android.toolchain.cmake ]; then
    echo "   NDK на месте"
else
    echo "   НЕТ NDK — поставь r26d (см. инструкцию)"; exit 1
fi
python3 - <<'PY'
import io
p = "android/app/build.gradle"
s = io.open(p, encoding="utf-8").read()
if "26.3.11579264" not in s:
    s = s.replace("ndkVersion '28.2.13676358'", "ndkVersion '26.3.11579264'")
    io.open(p, "w", encoding="utf-8").write(s)
    print("   ndkVersion → 26.3.11579264")
else:
    print("   ndkVersion уже исправлен")
PY
grep -n "max-page-size\|externalNativeBuild\|arguments" android/app/build.gradle | head -5 || true

step "1. Лицензии SDK (чтобы gradle не спросил в интерактиве)"
mkdir -p $ANDROID_HOME/licenses
printf "24333f8a63b6825ea9c5514f83c2829b004d1fee\n" > $ANDROID_HOME/licenses/android-sdk-license
printf "d56f5187479451eabf01fb78af6dfcb131a6481e\n" >> $ANDROID_HOME/licenses/android-sdk-license
printf "8933bad161af4178b1185d1a37fbf41ea5269c55\n" >> $ANDROID_HOME/licenses/android-sdk-license
printf "84831b9409646a918e30573bab4c9c91346d8abd\n" > $ANDROID_HOME/licenses/android-sdk-preview-license
echo "   ок"

if [ "$1" = "apk" ]; then skip_deps=1; fi
if [ -z "$skip_deps" ]; then
step "2. Кросс-сборка SDL3 + FreeType + OCCT (самый долгий шаг)"
if [ -f ~/Android/prefix/arm64-v8a/lib/libTKernel.so ]; then
    echo "   префикс OCCT уже есть — пропускаю (пересобрать: rm -rf ~/Android/prefix)"
else
    cd android && ./scripts/setup-deps.sh > /tmp/mz_deps.log 2>&1 \
        && echo "   ок (хвост лога:)" && tail -5 /tmp/mz_deps.log \
        || { echo "   ОШИБКА — хвост лога:"; tail -30 /tmp/mz_deps.log; exit 1; }
    cd ..
fi
fi

step "3. Gradle: скачивание wrapper (первый раз ~130 МБ) и сборка APK"
cd android
./gradlew assembleDebug -Dorg.gradle.jvmargs=-Xmx3g > /tmp/mz_gradle.log 2>&1 \
    && echo "   ок" || { echo "   ОШИБКА — хвост лога:"; tail -40 /tmp/mz_gradle.log; exit 1; }
APK=app/build/outputs/apk/debug/app-debug.apk
[ -f $APK ] || { echo "   APK не найден — пришли хвост /tmp/mz_gradle.log"; exit 1; }

step "4. Подпись (debug-ключ)"
KS=~/.android/debug.keystore
[ -f $KS ] || keytool -genkeypair -keystore $KS -storepass android -keypass android \
    -alias androiddebugkey -dname "CN=Android Debug" -keyalg RSA -validity 10000
$BT/zipalign -f 4 $APK /tmp/mz-aligned.apk
$BT/apksigner sign --ks $KS --ks-pass pass:android --key-pass pass:android \
    --out /tmp/materializr-ru.apk /tmp/mz-aligned.apk
ls -lh /tmp/materializr-ru.apk
echo
echo "ГОТОВО! APK: /tmp/materializr-ru.apk — ставь: adb install или просто скопируй на телефон"
