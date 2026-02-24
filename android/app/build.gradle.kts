// Android Project Build Configuration
// build.gradle.kts (Kotlin DSL)

plugins {
    id("com.android.application")
    kotlin("android")
    kotlin("kapt")
    id("dagger.hilt.android.plugin")
}

android {
    namespace = "com.neuroai.neurodrug"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.neuroai.neurodrug"
        minSdk = 28
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            buildConfigField("String", "API_URL", "\"https://api.neuroai.example.com/v1/\"")
            buildConfigField("String", "MODEL_CACHE_DIR", "\"/cache/models\"")
        }
        
        debug {
            isMinifyEnabled = false
            buildConfigField("String", "API_URL", "\"http://localhost:8000/api/v1/\"")
            buildConfigField("String", "MODEL_CACHE_DIR", "\"/cache/models\"")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
        freeCompilerArgs += listOf(
            "-opt-in=androidx.compose.material3.ExperimentalMaterial3Api",
            "-opt-in=androidx.compose.foundation.ExperimentalFoundationApi",
        )
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.3"
    }

    packagingOptions {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    // ========== COMPOSE & UI ==========
    val composeVersion = "1.5.3"
    val composeMaterialVersion = "1.0.1"
    
    implementation("androidx.compose.ui:ui:$composeVersion")
    implementation("androidx.compose.material3:material3:$composeMaterialVersion")
    implementation("androidx.compose.material:material-icons-extended:$composeVersion")
    implementation("androidx.compose.runtime:runtime:$composeVersion")
    implementation("androidx.activity:activity-compose:1.8.0")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.6.1")
    
    // ========== NAVIGATION ==========
    val navigationVersion = "2.7.2"
    implementation("androidx.navigation:navigation-compose:$navigationVersion")
    
    // ========== LIFECYCLE & VIEWMODEL ==========
    val lifecycleVersion = "2.6.1"
    implementation("androidx.lifecycle:lifecycle-viewmodel:$lifecycleVersion")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:$lifecycleVersion")
    implementation("androidx.lifecycle:lifecycle-runtime:$lifecycleVersion")
    
    // ========== DEPENDENCY INJECTION ==========
    val hiltVersion = "2.48"
    implementation("com.google.dagger:hilt-android:$hiltVersion")
    kapt("com.google.dagger:hilt-compiler:$hiltVersion")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")
    implementation("androidx.hilt:hilt-work:1.1.0")
    kapt("androidx.hilt:hilt-compiler:1.1.0")
    
    // ========== NETWORKING ==========
    val retrofitVersion = "2.10.0"
    implementation("com.squareup.retrofit2:retrofit:$retrofitVersion")
    implementation("com.squareup.retrofit2:converter-gson:$retrofitVersion")
    implementation("com.squareup.okhttp3:okhttp:4.11.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.11.0")
    
    // ========== LOCAL STORAGE ==========
    val roomVersion = "2.5.2"
    implementation("androidx.room:room-runtime:$roomVersion")
    kapt("androidx.room:room-compiler:$roomVersion")
    implementation("androidx.room:room-ktx:$roomVersion")
    
    implementation("androidx.datastore:datastore-preferences:1.0.0")
    
    // ========== SERIALIZATION ==========
    implementation("com.google.code.gson:gson:2.10.1")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
    
    // ========== ML & IMAGE PROCESSING ==========
    val tfLiteVersion = "2.13.0"
    implementation("org.tensorflow:tensorflow-lite:$tfLiteVersion")
    implementation("org.tensorflow:tensorflow-lite-metal:$tfLiteVersion")
    implementation("org.tensorflow:tensorflow-lite-gpu:$tfLiteVersion")
    
    // ========== BACKGROUND TASKS ==========
    val workVersion = "2.8.1"
    implementation("androidx.work:work-runtime-ktx:$workVersion")
    
    // ========== VISUALIZATION & GRAPHICS ==========
    implementation("com.github.PhilJay:MPAndroidChart:v3.1.0")
    implementation("androidx.graphics:graphics-core:1.0.0-alpha03")
    
    // ========== UTILITIES ==========
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.10.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    
    // ========== LOGGING & ANALYTICS ==========
    implementation("com.jakewharton.timber:timber:5.0.1")
    implementation("com.google.firebase:firebase-analytics-ktx:21.4.0")
    implementation("com.google.firebase:firebase-crashlytics-ktx:18.5.1")
    
    // ========== JSON SERIALIZATION FOR OFFLINE DATA ==========
    implementation("com.squareup.moshi:moshi-kotlin:${properties["moshi_version"]}") // Add to gradle.properties
    
    // ========== TESTING ==========
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.mockito.kotlin:mockito-kotlin:5.1.0")
    testImplementation("org.mockito:mockito-inline:5.2.0")
    testImplementation("androidx.arch.core:core-testing:2.2.0")
    
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4:$composeVersion")
    debugImplementation("androidx.compose.ui:ui-test-manifest:$composeVersion")
}

kapt {
    correctErrorTypes = true
}
