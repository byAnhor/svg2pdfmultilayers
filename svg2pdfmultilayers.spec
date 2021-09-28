# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['svg2pdfmultilayers.py'],
             pathex=['C:\\Users\\anita\\Documents\\GITHub\\svg2pdfmultilayers2'],
             binaries=[],
             datas=[('*.py', 'sources')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
             
a.datas += [('icon.ico','C:\\Users\\anita\\Documents\\GITHub\\svg2pdfmultilayers2\\icon.ico','DATA')]
a.datas += [('openXS.ico','C:\\Users\\anita\\Documents\\GITHub\\svg2pdfmultilayers2\\ressources\\openXS.ico','DATA')]
a.datas += [('savepdfXS.ico','C:\\Users\\anita\\Documents\\GITHub\\svg2pdfmultilayers2\\ressources\\savepdfXS.ico','DATA')]
a.datas += [('topdown.png','C:\\Users\\anita\\Documents\\GITHub\\svg2pdfmultilayers2\\ressources\\topdown.png','DATA')]
a.datas += [('leftright.png','C:\\Users\\anita\\Documents\\GITHub\\svg2pdfmultilayers2\\ressources\\leftright.png','DATA')]
a.datas += [('portrait.png','C:\\Users\\anita\\Documents\\GITHub\\svg2pdfmultilayers2\\ressources\\portrait.png','DATA')]
a.datas += [('landscape.png','C:\\Users\\anita\\Documents\\GITHub\\svg2pdfmultilayers2\\ressources\\landscape.png','DATA')]
a.datas += [('custoload.ico','C:\\Users\\anita\\Documents\\GITHub\\svg2pdfmultilayers2\\ressources\\custoload.ico','DATA')]
a.datas += [('custosave.ico','C:\\Users\\anita\\Documents\\GITHub\\svg2pdfmultilayers2\\ressources\\custosave.ico','DATA')]
a.datas += [('topleft.png','C:\\Users\\anita\\Documents\\GITHub\\svg2pdfmultilayers2\\ressources\\topleft.png','DATA')]
a.datas += [('center.png','C:\\Users\\anita\\Documents\\GITHub\\svg2pdfmultilayers2\\ressources\\center.png','DATA')]
a.datas += [('nocanvas.svg','C:\\Users\\anita\\Documents\\GITHub\\svg2pdfmultilayers2\\ressources\\nocanvas.svg','DATA')]
             
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
             
splash = Splash('ressources/splach.png',
                binaries=a.binaries,
                datas=a.datas,
                text_pos=(10, 50),
                text_size=12,
                text_color='black')
exe = EXE(pyz,
          splash,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='svg2pdfmultilayers',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='icon.ico')
