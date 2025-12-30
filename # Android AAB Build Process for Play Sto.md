# Android Apk Build Process



## Prerequisites

- Expo account (logged in via `eas login` account adeazhar.b@gmail.com password : Facebook1234)

- Node.js installed

- Access to GitHub Codespace



## Working Configuration (Tested)

- **Expo SDK**: 52.0.36

- **Android API Level**: 35

- **Kotlin Version**: 1.9.25



---



## Step 1: Update app.json



Ensure your `app.json` has these settings:



```json

{

    "expo": {

        "name": "HSE Plan MS",

        "slug": "hse-plan",

        "version": "1.0.0",

        "plugins": [

            [

                "expo-build-properties",

                {

                    "android": {

                        "compileSdkVersion": 35,

                        "targetSdkVersion": 35,

                        "kotlinVersion": "1.9.25"

                    }

                }

            ]

        ]

    }

}

```



**Key settings:**

- `compileSdkVersion: 35` - Required by Play Store

- `targetSdkVersion: 35` - Required by Play Store  

- `kotlinVersion: "1.9.25"` - Fixes Kotlin compilation errors



---



## Step 2: Update package.json



Use exact Expo version:



```json

{

    "dependencies": {

        "expo": "52.0.36",

        "expo-build-properties": "~0.13.0",

        "expo-asset": "~11.0.0",

        "expo-splash-screen": "~0.29.0"

    }

}

```



---



## Step 3: Build Commands



// turbo-all



```bash

# Install dependencies

npm install



# Initialize EAS (if not done)

eas init



# Build APK for Preview

eas build --platform android --profile preview --clear-cache

```



---



## Step 4: Download APK



After build completes:

1. EAS provides download URL

2. Download the `.apk` file

---



## Troubleshooting



### Error: Kotlin compilation failed

**Solution:** Add `"kotlinVersion": "1.9.25"` to expo-build-properties



### Error: expo-asset not found  

**Solution:** Add `"expo-asset": "~11.0.0"` to dependencies



### Error: splashscreen_background not found

**Solution:** Add `"expo-splash-screen": "~0.29.0"` to dependencies



### Error: Invalid UUID appId

**Solution:** Remove `extra.eas.projectId` from app.json and run `eas init`



---



## Version History

- **v5 (2025-12-13)**: Working build with Expo 52.0.36, API 35, Kotlin 1.9.25