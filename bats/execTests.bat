c: && cd \Users\sanma\AppData\Local\Android\Sdk\platform-tools

adb shell am instrument -w -r -e listener de.schroepf.androidxmlrunlistener.XmlRunListener  -e debug false com.example.app1.test/androidx.test.runner.AndroidJUnitRunner
