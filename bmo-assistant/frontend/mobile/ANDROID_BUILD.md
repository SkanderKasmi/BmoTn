# BMO Android App (APK)

## Overview

The Android version of BMO uses React Native to create a native Android application.

## Prerequisites

- Node.js 18+
- Android Studio
- Java JDK 11+
- React Native CLI

## Setup

### 1. Install React Native CLI

```bash
npm install -g react-native-cli
```

### 2. Initialize React Native Project

```bash
cd frontend/mobile
npx react-native init BMOAssistant
```

### 3. Configuration

Update `android/app/build.gradle`:

```gradle
android {
    compileSdkVersion 33
    
    defaultConfig {
        applicationId "com.bmoassistant"
        minSdkVersion 21
        targetSdkVersion 33
        versionCode 1
        versionName "1.0"
    }
    
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

### 4. Permissions (AndroidManifest.xml)

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

## Building APK

### Debug APK (for testing)

```bash
cd android
./gradlew assembleDebug
```

APK location: `android/app/build/outputs/apk/debug/app-debug.apk`

### Release APK (for distribution)

1. Generate signing key:

```bash
keytool -genkeypair -v -storetype PKCS12 -keystore bmo-release-key.keystore -alias bmo-key-alias -keyalg RSA -keysize 2048 -validity 10000
```

2. Update `android/gradle.properties`:

```properties
MYAPP_RELEASE_STORE_FILE=bmo-release-key.keystore
MYAPP_RELEASE_KEY_ALIAS=bmo-key-alias
MYAPP_RELEASE_STORE_PASSWORD=your-store-password
MYAPP_RELEASE_KEY_PASSWORD=your-key-password
```

3. Update `android/app/build.gradle`:

```gradle
android {
    signingConfigs {
        release {
            storeFile file(MYAPP_RELEASE_STORE_FILE)
            storePassword MYAPP_RELEASE_STORE_PASSWORD
            keyAlias MYAPP_RELEASE_KEY_ALIAS
            keyPassword MYAPP_RELEASE_KEY_PASSWORD
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

4. Build release APK:

```bash
cd android
./gradlew assembleRelease
```

APK location: `android/app/build/outputs/apk/release/app-release.apk`

## Android-Specific Features

### 1. Voice Recognition

Uses Android native speech recognition API for faster processing.

### 2. App Launching

Android intents are used to launch apps directly:

```javascript
import { Linking } from 'react-native';

// Open YouTube
Linking.openURL('intent://www.youtube.com#Intent;scheme=https;package=com.google.android.youtube;end');

// Open WhatsApp
Linking.openURL('whatsapp://send');
```

### 3. Background Service

BMO can run in the background and respond to voice commands:

```javascript
import BackgroundService from 'react-native-background-actions';

const backgroundTask = async (taskDataArguments) => {
    // Listen for "BMO" wake word
    // Process commands
};

BackgroundService.start(backgroundTask, options);
```

### 4. Floating Widget

BMO's face can appear as a floating bubble on the screen:

- Uses `SYSTEM_ALERT_WINDOW` permission
- Can be moved around the screen
- Always on top of other apps

## Installation on Device

### Via ADB

```bash
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

### Via File Transfer

1. Copy APK to device
2. Enable "Install from Unknown Sources" in Settings
3. Tap the APK file to install

## Testing

```bash
# Run on connected device
npx react-native run-android

# Run on emulator
npx react-native run-android --emulator
```

## Distribution

1. **Google Play Store**: Upload release APK to Google Play Console
2. **Direct Download**: Host APK file on your server
3. **TestFlight**: Use Firebase App Distribution for beta testing

## Troubleshooting

### Common Issues

1. **Build fails**: Clean build
```bash
cd android
./gradlew clean
```

2. **Permission denied**: 
```bash
chmod +x android/gradlew
```

3. **Metro bundler issues**:
```bash
npx react-native start --reset-cache
```

## Size Optimization

- Enable ProGuard
- Use app bundles (.aab) instead of APK
- Remove unused resources
- Enable code shrinking

Final APK size: ~15-20 MB
