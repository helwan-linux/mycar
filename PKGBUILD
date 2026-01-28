# Maintainer: Helwan Linux Team <helwanlinux@gmail.com>
pkgname=hel-mycar
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
    # الدخول للمجلد الذي تم تحميله من GitHub
    cd "$srcdir/mycar"

    # إنشاء المسارات اللازمة في النظام
    install -d "$pkgdir/usr/share/hel-mycar"
    install -d "$pkgdir/usr/bin"
    install -d "$pkgdir/usr/share/applications"
    install -d "$pkgdir/usr/share/pixmaps"

    # نسخ محتويات مجلد car بالكامل (الذي يحتوي على main.py و Assets)
    cp -r car/* "$pkgdir/usr/share/hel-mycar/"

    # إنشاء سكربت التشغيل بالاسم الجديد hel-mycar
    echo -e "#!/bin/bash\ncd /usr/share/hel-mycar && python main.py" > "$pkgdir/usr/bin/hel-mycar"
    chmod +x "$pkgdir/usr/bin/hel-mycar"

    # تثبيت الأيقونة من داخل مجلد car/Assets
    install -m644 car/Assets/car_dodge.png "$pkgdir/usr/share/pixmaps/hel-mycar.png"

    # إنشاء ملف الـ Desktop Entry للظهور في القائمة
    cat <<EOF > "$pkgdir/usr/share/applications/hel-mycar.desktop"
[Desktop Entry]
Name=Helwan MyCar
Comment=Race and dodge obstacles
Exec=hel-mycar
Icon=hel-mycar
Terminal=false
Type=Application
Categories=Game;ArcadeGame;
EOF
}
