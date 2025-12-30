# Android APK Build Rules & Implementation Plan

**Version:** 2.0 (Secure Release)
**Date:** 2025-12-31
**Objective:** Build a production-grade, secure Android APK with obfuscation and data protection enabled.

---

## 1. Prerequisites & Access

| Resource | Credential / Requirement |
| :--- | :--- |
| **Expo Account** | Email: `adeazhar.b@gmail.com` <br> Pass: `Facebook1234` |
| **Environment** | GitHub Codespace (Recommended) or Local Node.js Environment |
| **CLI Tool** | EAS CLI (`npm install -g eas-cli`) |
| **Engine** | **Hermes** (Must be enabled for bytecode security) |

---

## 2. Configuration Rules (Mandatory)

All builds must adhere to the following versioning and security standards to ensure Play Store compliance and application security.

### A. Version Standards
- **Expo SDK**: `52.0.36` (Exact match required)
- **Android API Level**: `35`
- **Kotlin Version**: `1.9.25`
- **Expo Build Properties**: `~0.13.0`

### B. Security Policies
1.  **Code Obfuscation**: ProGuard/R8 must be enabled for all release builds.
2.  **Data Protection**: ADB Backup must be set to `false` to prevent local data extraction.
3.  **JS Engine**: Hermes must be used to compile JavaScript to bytecode.

---

## 3. Implementation Steps

### Step 1: `app.json` Configuration
Update the `expo` object to include the required build properties and security settings.

```json
{
  "expo": {
    "name": "HSE Plan MS",
    "slug": "hse-plan",
    "version": "1.0.0",
    "jsEngine": "hermes",
    "plugins": [
      [
        "expo-build-properties",
        {
          "android": {
            "compileSdkVersion": 35,
            "targetSdkVersion": 35,
            "kotlinVersion": "1.9.25",
            "enableProguardInReleaseBuilds": true,
            "allowBackup": false,
            "extraProguardRules": "-keep class com.facebook.react.** { *; } -keep class com.facebook.flipper.** { *; } -keepattributes *Annotation*"
          }
        }
      ]
    ]
  }
}

Step 2: package.json DependenciesEnsure these exact versions are present to prevent build conflicts.JSON{
  "dependencies": {
    "expo": "52.0.36",
    "expo-build-properties": "~0.13.0",
    "expo-asset": "~11.0.0",
    "expo-splash-screen": "~0.29.0"
  }
}
Step 3: eas.json Build ProfilesDefine a production profile that enforces the "release" build type (triggers ProGuard).JSON{
  "build": {
    "preview": {
      "android": {
        "buildType": "apk"
      }
    },
    "production-apk": {
      "android": {
        "buildType": "apk",
        "gradleCommand": ":app:assembleRelease"
      },
      "env": {
        "EXPO_NO_TELEMETRY": "1"
      }
    }
  }
}
4. Execution CommandRun the following commands in order. Do not use the standard preview profile, as it skips security optimization.Bash# 1. Clean install to ensure dependency integrity
npm install

# 2. Login to EAS (if not already logged in)
eas login

# 3. Initialize EAS Project (only if this is the first time)
# Note: If you get "Invalid UUID" error, remove 'extra.eas.projectId' from app.json first
eas init

# 4. Build Secure APK
eas build --platform android --profile production-apk --clear-cache
5. Troubleshooting GuideError MessageCauseSolutionKotlin compilation failedVersion mismatchVerify kotlinVersion": "1.9.25" is in app.json.ClassNotFoundExceptionAggressive ObfuscationAdd the missing class to "extraProguardRules" in app.json.expo-asset not foundMissing DependencyRun npm install expo-asset@~11.0.0.splashscreen_backgroundMissing DependencyRun npm install expo-splash-screen@~0.29.0.Invalid UUID appIdProject ID ConflictDelete extra.eas.projectId from app.json and rerun eas init.
