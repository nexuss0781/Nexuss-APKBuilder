import os
import sys
import subprocess
import shutil
import urllib.request
import zipfile
from PIL import Image

# --- CONFIGURATION ---
BUILD_DIR = os.path.abspath("temp_build")
SDK_DIR = "/opt/android-sdk"
GRADLE_VERSION = "8.2.1" # Compatible with Java 17 & SDK 33
GRADLE_URL = f"https://services.gradle.org/distributions/gradle-{GRADLE_VERSION}-bin.zip"
GRADLE_LOCAL_DIR = os.path.abspath(f"gradle-{GRADLE_VERSION}")
GRADLE_EXE = os.path.join(GRADLE_LOCAL_DIR, "bin", "gradle")

# ANSI Colors
C_CYAN = "\033[96m"
C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_RESET = "\033[0m"
C_BOLD = "\033[1m"

def log(msg): print(f"{C_CYAN}[SYSTEM]{C_RESET} {msg}")
def success(msg): print(f"{C_GREEN}[SUCCESS]{C_RESET} {C_BOLD}{msg}{C_RESET}")
def error(msg): print(f"{C_RED}[ERROR]{C_RESET} {msg}")

def ensure_gradle():
    """Ensures a compatible Gradle version is present."""
    if os.path.exists(GRADLE_EXE):
        return GRADLE_EXE
    
    log(f"System Gradle is too old. Downloading Gradle {GRADLE_VERSION} (Portable)...")
    zip_path = "gradle_dist.zip"
    
    try:
        # Download
        urllib.request.urlretrieve(GRADLE_URL, zip_path)
        log("Extracting Gradle...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Cleanup Zip
        os.remove(zip_path)
        
        # Make executable
        st = os.stat(GRADLE_EXE)
        os.chmod(GRADLE_EXE, st.st_mode | 0o111)
        
        success("Gradle portable installed.")
        return GRADLE_EXE
    except Exception as e:
        error(f"Failed to setup Gradle: {e}")
        sys.exit(1)

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())

def get_inputs():
    print(f"{C_BOLD}--- MIDNIGHT OBSIDIAN BUILDER (PORTABLE ENGINE) ---{C_RESET}")
    app_name = input(f"{C_CYAN}?> App Name:{C_RESET} ").strip()
    url = input(f"{C_CYAN}?> Website URL:{C_RESET} ").strip()
    icon_path = input(f"{C_CYAN}?> Path to Icon (png/jpg):{C_RESET} ").strip()
    
    safe_name = "".join(c for c in app_name if c.isalnum()).lower()
    if not safe_name: safe_name = "myapp"
    package_name = f"com.{safe_name}.web"
    
    return app_name, url, icon_path, package_name

# --- TEMPLATES ---

def generate_manifest(package_name, app_name):
    return f"""
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package_name}">
    <uses-permission android:name="android.permission.INTERNET" />
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="{app_name}"
        android:roundIcon="@mipmap/ic_launcher"
        android:supportsRtl="true"
        android:theme="@style/AppTheme">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""

def generate_gradle_build(package_name):
    # Modern Gradle 8.x + AGP 8.1.0 (Compatible with Java 17)
    return f"""
plugins {{
    id 'com.android.application' version '8.1.0'
}}

android {{
    namespace '{package_name}'
    compileSdk 33

    defaultConfig {{
        applicationId "{package_name}"
        minSdk 24
        targetSdk 33
        versionCode 1
        versionName "1.0"
    }}

    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}
}}

repositories {{
    google()
    mavenCentral()
}}

dependencies {{
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.swiperefreshlayout:swiperefreshlayout:1.1.0'
}}
"""

def generate_styles():
    return """
<resources>
    <style name="AppTheme" parent="Theme.MaterialComponents.DayNight.NoActionBar">
        <item name="colorPrimary">#121212</item>
        <item name="colorPrimaryVariant">#000000</item>
        <item name="colorOnPrimary">#FFFFFF</item>
        <item name="colorSecondary">#00E5FF</item>
        <item name="android:statusBarColor">#000000</item>
        <item name="android:windowBackground">#121212</item>
        <item name="android:forceDarkAllowed">true</item>
    </style>
</resources>
"""

def generate_layout():
    return """
<?xml version="1.0" encoding="utf-8"?>
<androidx.coordinatorlayout.widget.CoordinatorLayout 
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#121212">

    <com.google.android.material.appbar.AppBarLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:theme="@style/ThemeOverlay.AppCompat.Dark.ActionBar">

        <androidx.appcompat.widget.Toolbar
            android:id="@+id/toolbar"
            android:layout_width="match_parent"
            android:layout_height="?attr/actionBarSize"
            android:background="#121212"
            app:popupTheme="@style/ThemeOverlay.AppCompat.Light" />
            
        <ProgressBar
            android:id="@+id/progressBar"
            style="?android:attr/progressBarStyleHorizontal"
            android:layout_width="match_parent"
            android:layout_height="4dp"
            android:indeterminate="false"
            android:progressDrawable="@drawable/neon_progress"
            android:visibility="gone" />

    </com.google.android.material.appbar.AppBarLayout>

    <androidx.swiperefreshlayout.widget.SwipeRefreshLayout
        android:id="@+id/swipeRefresh"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        app:layout_behavior="@string/appbar_scrolling_view_behavior">

        <WebView
            android:id="@+id/webView"
            android:layout_width="match_parent"
            android:layout_height="match_parent" />

    </androidx.swiperefreshlayout.widget.SwipeRefreshLayout>

</androidx.coordinatorlayout.widget.CoordinatorLayout>
"""

def generate_neon_progress():
    return """
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:id="@android:id/background">
        <shape><solid android:color="#121212"/></shape>
    </item>
    <item android:id="@android:id/progress">
        <clip><shape><solid android:color="#00E5FF"/></shape></clip>
    </item>
</layer-list>
"""

def generate_java(package_name, target_url):
    return f"""
package {package_name};

import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.view.HapticFeedbackConstants;
import android.view.View;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ProgressBar;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;
import android.view.Menu;
import android.view.MenuItem;

public class MainActivity extends AppCompatActivity {{

    private WebView webView;
    private SwipeRefreshLayout swipeRefresh;
    private ProgressBar progressBar;
    private final String TARGET_URL = "{target_url}";

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        progressBar = findViewById(R.id.progressBar);
        swipeRefresh = findViewById(R.id.swipeRefresh);
        webView = findViewById(R.id.webView);

        setupWebView();
        setupSwipeRefresh();
        
        if (savedInstanceState == null) {{
            webView.loadUrl(TARGET_URL);
        }}
    }}

    private void setupWebView() {{
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setForceDark(WebSettings.FORCE_DARK_ON);

        webView.setWebViewClient(new WebViewClient() {{
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {{
                progressBar.setVisibility(View.VISIBLE);
                progressBar.setProgress(0);
            }}
            @Override
            public void onPageFinished(WebView view, String url) {{
                progressBar.setVisibility(View.GONE);
                swipeRefresh.setRefreshing(false);
            }}
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {{
                return false;
            }}
        }});

        webView.setWebChromeClient(new WebChromeClient() {{
            @Override
            public void onProgressChanged(WebView view, int newProgress) {{
                progressBar.setProgress(newProgress);
            }}
        }});
    }}

    private void setupSwipeRefresh() {{
        swipeRefresh.setColorSchemeColors(0xFF00E5FF);
        swipeRefresh.setProgressBackgroundColorSchemeColor(0xFF121212);
        swipeRefresh.setOnRefreshListener(() -> {{
            swipeRefresh.performHapticFeedback(HapticFeedbackConstants.VIRTUAL_KEY);
            webView.reload();
        }});
    }}

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {{
        menu.add(0, 1, 0, "Share");
        menu.add(0, 2, 0, "Clear Cache");
        menu.add(0, 3, 0, "Home");
        return true;
    }}

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {{
        switch (item.getItemId()) {{
            case 1:
                Intent shareIntent = new Intent(Intent.ACTION_SEND);
                shareIntent.setType("text/plain");
                shareIntent.putExtra(Intent.EXTRA_TEXT, webView.getUrl());
                startActivity(Intent.createChooser(shareIntent, "Share via"));
                return true;
            case 2:
                webView.clearCache(true);
                webView.reload();
                return true;
            case 3:
                webView.loadUrl(TARGET_URL);
                return true;
        }}
        return super.onOptionsItemSelected(item);
    }}

    @Override
    public void onBackPressed() {{
        if (webView.canGoBack()) {{
            webView.goBack();
        }} else {{
            super.onBackPressed();
        }}
    }}
}}
"""

def process_icons(source_path, res_dir):
    try:
        img = Image.open(source_path).convert("RGBA")
        sizes = {
            "mipmap-mdpi": (48, 48),
            "mipmap-hdpi": (72, 72),
            "mipmap-xhdpi": (96, 96),
            "mipmap-xxhdpi": (144, 144),
            "mipmap-xxxhdpi": (192, 192)
        }
        for folder, size in sizes.items():
            path = os.path.join(res_dir, folder)
            os.makedirs(path, exist_ok=True)
            resized_img = img.resize(size, Image.Resampling.LANCZOS)
            resized_img.save(os.path.join(path, "ic_launcher.png"))
        log("Icons generated.")
    except Exception as e:
        error(f"Icon processing failed: {e}")
        sys.exit(1)

def main():
    # 1. BOOTSTRAP: Get working Gradle
    gradle_bin = ensure_gradle()
    
    # 2. INPUTS
    app_name, url, icon_path, package_name = get_inputs()
    
    # 3. SCAFFOLDING
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    
    app_dir = os.path.join(BUILD_DIR, "app")
    main_dir = os.path.join(app_dir, "src", "main")
    java_dir = os.path.join(main_dir, "java", *package_name.split("."))
    res_dir = os.path.join(main_dir, "res")
    
    log("Writing source code...")
    
    create_file(os.path.join(BUILD_DIR, "settings.gradle"), f"rootProject.name = '{app_name}'\ninclude ':app'")
    create_file(os.path.join(BUILD_DIR, "local.properties"), f"sdk.dir={SDK_DIR}")
    # Fix for memory constraint
    create_file(os.path.join(BUILD_DIR, "gradle.properties"), "org.gradle.jvmargs=-Xmx1536m -Dfile.encoding=UTF-8")
    
    create_file(os.path.join(app_dir, "build.gradle"), generate_gradle_build(package_name))
    create_file(os.path.join(main_dir, "AndroidManifest.xml"), generate_manifest(package_name, app_name))
    create_file(os.path.join(java_dir, "MainActivity.java"), generate_java(package_name, url))
    create_file(os.path.join(res_dir, "values", "styles.xml"), generate_styles())
    create_file(os.path.join(res_dir, "layout", "activity_main.xml"), generate_layout())
    create_file(os.path.join(res_dir, "drawable", "neon_progress.xml"), generate_neon_progress())
    
    # 4. IMAGES
    process_icons(icon_path, res_dir)
    
    # 5. BUILD
    log("Starting build with Portable Gradle... (First run downloads dependencies)")
    try:
        cmd = [gradle_bin, "assembleDebug", "--no-daemon", "--stacktrace"]
        subprocess.run(cmd, cwd=BUILD_DIR, check=True)
    except subprocess.CalledProcessError:
        error("Build Failed. See logs above.")
        return

    # 6. EXPORT
    output_apk = os.path.join(BUILD_DIR, "app", "build", "outputs", "apk", "debug", "app-debug.apk")
    final_name = f"{app_name.replace(' ', '_')}.apk"
    
    if os.path.exists(output_apk):
        shutil.move(output_apk, final_name)
        shutil.rmtree(BUILD_DIR)
        success(f"Build Complete! Download {final_name} now.")
    else:
        error("APK not found after build.")

if __name__ == "__main__":
    main()
