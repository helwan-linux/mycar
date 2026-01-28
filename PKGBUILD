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
    cd "$srcdir/mycar"

    # 1. إنشاء المسارات في النظام
    install -d "$pkgdir/usr/share/helwan-mycar"
    install -d "$pkgdir/usr/bin"
    install -d "$pkgdir/usr/share/applications"
    install -d "$pkgdir/usr/share/pixmaps"

    # 2. نسخ ملفات اللعبة (Assets والسكربتات)
    cp -r * "$pkgdir/usr/share/helwan-mycar/"

    # 3. إنشاء سكربت تشغيل في /usr/bin لتسهيل الاستدعاء
    echo -e "#!/bin/bash\ncd /usr/share/helwan-mycar && python main.py" > "$pkgdir/usr/bin/helwan-mycar"
    chmod +x "$pkgdir/usr/bin/helwan-mycar"

    # 4. تثبيت الأيقونة (بفرض وجود أيقونة باسم car_dodge.png في Assets)
    install -m644 Assets/car_dodge.png "$pkgdir/usr/share/pixmaps/helwan-mycar.png"

    # 5. إنشاء ملف الـ Desktop Entry لتظهر في القائمة
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
