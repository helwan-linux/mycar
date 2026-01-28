# Maintainer: Helwan Linux Team <helwanlinux@gmail.com>
pkgname=helwan-mycar
pkgver=1.0
pkgrel=1
pkgdesc="A simple 2D car dodging game for Helwan Linux"
arch=('any')
url="https://github.com/helwan-linux/mycar"
license=('GPL')
depends=('python' 'python-pygame')
source=("git+https://github.com/helwan-linux/mycar.git")
md5sums=('SKIP')

package() {
    # الدخول للمجلد اللي نزل من جيت هاب
    cd "$srcdir/mycar"

    # إنشاء المسارات في النظام
    install -d "$pkgdir/usr/share/helwan-mycar"
    install -d "$pkgdir/usr/bin"
    install -d "$pkgdir/usr/share/applications"
    install -d "$pkgdir/usr/share/pixmaps"

    # نسخ محتويات مجلد car بالكامل إلى مسار البرنامج
    # لاحظ إننا بننسخ اللي "جوه" مجلد car عشان main.py يبقى في الجذر بتاع helwan-mycar
    cp -r car/* "$pkgdir/usr/share/helwan-mycar/"

    # إنشاء سكربت التشغيل
    echo -e "#!/bin/bash\ncd /usr/share/helwan-mycar && python main.py" > "$pkgdir/usr/bin/helwan-mycar"
    chmod +x "$pkgdir/usr/bin/helwan-mycar"

    # تثبيت الأيقونة (الموجودة داخل car/Assets/)
    install -m644 car/Assets/car_dodge.png "$pkgdir/usr/share/pixmaps/helwan-mycar.png"

    # إنشاء ملف الـ Desktop Entry
    cat <<EOF > "$pkgdir/usr/share/applications/helwan-mycar.desktop"
[Desktop Entry]
Name=Helwan MyCar
Comment=Race and dodge obstacles
Exec=helwan-mycar
Icon=helwan-mycar
Terminal=false
Type=Application
Categories=Game;ArcadeGame;
EOF
}
