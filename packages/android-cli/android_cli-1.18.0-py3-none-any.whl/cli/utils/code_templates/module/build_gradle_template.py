def create_build_gradle(name):
    file_name = "build.gradle.kts"
    file_content = f'''import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {{
    id("com.android.library")
    id("kotlin-android")
    id("androidx.navigation.safeargs.kotlin")
    id("com.google.devtools.ksp")
    alias(libs.plugins.compose.compiler)
    `android-config`
}}

android {{
    namespace = "com.astropaycard.android.feature.{name}"

    flavorDimensions.add("default")

    productFlavors {{
        create("production") {{
            dimension = "default"
        }}
        create("tst") {{
            dimension = "default"
        }}
         create("staging") {{
            dimension = "default"
        }}
    }}

    buildTypes {{
        getByName("debug") {{
        }}

        getByName("release") {{
            proguardFile("proguard-rules.pro")
        }}
    }}
    buildFeatures {{
        compose = true
        viewBinding = true
    }}
}}

dependencies {{
    implementation(project(":domain"))
    implementation(project(":infrastructure"))
    implementation(project(":core:common"))
    implementation(project(":core:base"))
    implementation(project(":core:design-system"))
    implementation(project(":core:ui"))

    implementation(libs.bundles.compose)

    implementation(platform(libs.koin.bom))
    implementation(libs.koin.android)

    implementation(libs.navigation.fragment.ktx)

    testImplementation(libs.junit)
    testImplementation(libs.mockk)
    testImplementation(libs.coroutines.test)
    testImplementation(libs.kluent)
    testImplementation(libs.core.testing)
}}
'''
    with open(file_name, "w") as file:
        file.write(file_content)
