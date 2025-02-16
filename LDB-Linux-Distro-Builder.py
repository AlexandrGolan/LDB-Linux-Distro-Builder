import os
import subprocess
import sys
from PyQt5 import QtWidgets, uic

class LinuxDistroBuilder(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.theme_box = self.findChild(QtWidgets.QComboBox, 'theme_box')
        self.theme_box.addItems(['Light', 'Dark'])
        self.theme_box.currentIndexChanged.connect(self.change_theme)
        self.made_by_label = QtWidgets.QLabel('Made by: Golan_Alexandr & Alexeev_dev', self)
        self.made_by_label.setStyleSheet('color: black; position: absolute; left: 10px; bottom: 10px;')
        self.made_by_label.raise_()  # Используем Qt Designer для GUI
        self.setWindowTitle('Linux Distro Builder')

        # Привязка кнопок
        self.build_button.clicked.connect(self.build_distro)
        self.install_mode_box = self.findChild(QtWidgets.QComboBox, 'install_mode_box')
        self.color_theme_box = self.findChild(QtWidgets.QComboBox, 'color_theme_box')
        self.add_utility_button.clicked.connect(self.add_utility)
        self.background_image_path = None
        self.utility_list = []
        self.shell_box = self.findChild(QtWidgets.QComboBox, 'shell_box')
        self.desktop_env_box = self.findChild(QtWidgets.QComboBox, 'desktop_env_box')
        self.bootloader_box = self.findChild(QtWidgets.QComboBox, 'bootloader_box')
        self.pkg_manager_box = self.findChild(QtWidgets.QComboBox, 'pkg_manager_box')
        self.plymouth_box = self.findChild(QtWidgets.QComboBox, 'plymouth_box')
        self.repo_box.addItems(['Ubuntu', 'Debian', 'Arch', 'Fedora', 'Gentoo'])
        self.install_mode_box.addItems(['No GUI', 'With GUI'])
        self.color_theme_box.addItems(['Light', 'Dark'])
        self.shell_box.addItems(['bash', 'zsh'])
        self.desktop_env_box.addItems(['XFCE', 'GNOME', 'CLI', 'KDE Plasma', 'Basic Desktop'])
        self.bootloader_box.addItems(['GRUB', 'Syslinux', 'systemd-boot'])
        self.pkg_manager_box.addItems(['apt', 'dnf', 'pacman', 'portage'])
        self.plymouth_box.addItems(['Default', 'Dark тема', 'None'])

    def add_utility(self):
        file_dialog = QtWidgets.QFileDialog()
        utility_path, _ = file_dialog.getOpenFileName(self, 'Select utility package')
        if utility_path:
            self.utility_list.append(utility_path)
            self.output_text.append(f'Utility added: {utility_path}')

    def change_theme(self):
        theme = self.theme_box.currentText()
        if theme == 'Dark':
            self.setStyleSheet('background-color: #2b2b2b; color: white;')
            self.made_by_label.setStyleSheet('color: white; position: absolute; left: 10px; bottom: 10px;')
        else:
            self.setStyleSheet('background-color: white; color: black;')
            self.made_by_label.setStyleSheet('color: black; position: absolute; left: 10px; bottom: 10px;')

    def build_distro(self):
        repo = self.repo_box.currentText()
        distro_name = self.name_input.text()

        if not distro_name:
            self.output_text.setText('Enter the name of the distro!')
            return

        self.output_text.setText(f'Starting the build of the distro {distro_name} based on {repo}...')

        try:
            os.makedirs(f'./{distro_name}', exist_ok=True)
            if repo == 'Ubuntu' or repo == 'Debian':
                subprocess.run(['debootstrap', '--arch', 'amd64', 'stable', f'./{distro_name}', 'http://deb.debian.org/debian/'])
            elif repo == 'Arch':
                subprocess.run(['pacstrap', f'./{distro_name}', 'base'])
            elif repo == 'Fedora':
                subprocess.run(['dnf', 'installroot', f'./{distro_name}', 'install', 'fedora-release'])
            elif repo == 'Gentoo':
                subprocess.run(['wget', '-O', f'./{distro_name}/stage3.tar.xz', 'https://bouncer.gentoo.org/fetch/root/all/releases/amd64/autobuilds/current-stage3-amd64/stage3-amd64-latest.tar.xz'])
                subprocess.run(['tar', 'xpf', f'./{distro_name}/stage3.tar.xz', '-C', f'./{distro_name}'])

            self.output_text.setText('Build completed. Installing the bootloader...')

            bootloader = self.bootloader_box.currentText()
            if bootloader == 'GRUB':
                subprocess.run(['grub-install', '--root-directory', f'./{distro_name}', '/dev/sda'])
                subprocess.run(['grub-mkconfig', '-o', f'./{distro_name}/boot/grub/grub.cfg'])
            elif bootloader == 'Syslinux':
                subprocess.run(['syslinux', '--install', f'./{distro_name}/boot/syslinux'])
            elif bootloader == 'systemd-boot':
                subprocess.run(['bootctl', '--path', f'./{distro_name}/boot', 'install'])

            self.output_text.setText('Installing Plymouth theme...')
            plymouth = self.plymouth_box.currentText()
            if plymouth == 'Стандартная':
                subprocess.run(['apt', 'install', '-y', 'plymouth-theme-spinner'], cwd=f'./{distro_name}')
            elif plymouth == 'Dark тема':
                subprocess.run(['apt', 'install', '-y', 'plymouth-theme-script'], cwd=f'./{distro_name}')

            self.output_text.setText('Installing terminal shell...')
            shell = self.shell_box.currentText()
            if shell == 'bash':
                subprocess.run(['chroot', f'./{distro_name}', 'apt', 'install', '-y', 'bash'])
            elif shell == 'zsh':
                subprocess.run(['chroot', f'./{distro_name}', 'apt', 'install', '-y', 'zsh'])

            self.output_text.setText('Installing desktop environment...')
            desktop_env = self.desktop_env_box.currentText()
            if desktop_env == 'XFCE':
                subprocess.run(['chroot', f'./{distro_name}', 'apt', 'install', '-y', 'xfce4'])
            elif desktop_env == 'GNOME':
                subprocess.run(['chroot', f'./{distro_name}', 'apt', 'install', '-y', 'gnome'])
            elif desktop_env == 'KDE Plasma':
                subprocess.run(['chroot', f'./{distro_name}', 'apt', 'install', '-y', 'plasma-desktop'])
            elif desktop_env == 'Basic Desktop':
                subprocess.run(['chroot', f'./{distro_name}', 'apt', 'install', '-y', 'xorg', 'lightdm', 'openbox'])
                subprocess.run(['chroot', f'./{distro_name}', 'apt', 'install', '-y', 'plasma-desktop'])

            self.output_text.setText('Installing utilities...')
            for utility in self.utility_list:
                subprocess.run(['cp', utility, f'./{distro_name}/opt/'])
                subprocess.run(['chroot', f'./{distro_name}', 'dpkg', '-i', f'/opt/{os.path.basename(utility)}'])

            install_mode = self.install_mode_box.currentText()
            if install_mode == 'С GUI':
                bg_dialog = QtWidgets.QFileDialog()
                self.background_image_path, _ = bg_dialog.getOpenFileName(self, 'Select background image (PNG)')
                if self.background_image_path:
                    subprocess.run(['cp', self.background_image_path, f'./{distro_name}/usr/share/installer-bg.png'])

                color_theme = self.color_theme_box.currentText()
                if color_theme == 'Light':
                    subprocess.run(['sed', '-i', 's/dark/light/g', f'./{distro_name}/debian-installer/theme.cfg'])
                elif color_theme == 'Dark':
                    subprocess.run(['sed', '-i', 's/light/dark/g', f'./{distro_name}/debian-installer/theme.cfg'])

            self.output_text.setText('Starting ISO creation...')
            subprocess.run(['mkisofs', '-o', f'{distro_name}.iso', '-b', 'boot/grub/stage2_eltorito', '-no-emul-boot', '-boot-load-size', '4', '-boot-info-table', f'./{distro_name}'])

            self.output_text.setText(f'Distro {distro_name} successfully created! ISO image: {distro_name}.iso')
        except Exception as e:
            self.output_text.setText(f'Error: {str(e)}')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = LinuxDistroBuilder()
    window.show()
    sys.exit(app.exec_())
