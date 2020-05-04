# kivy_pong

Improved https://kivy.org/doc/stable/tutorials/pong.html

1. Game mechanics changed.
2. Game menu added.

## Create a package for Windows

https://kivy.org/doc/stable/guide/packaging-windows.html

1. Open your command line shell.
2. Create a folder into which the packaged app will be created. For example create a **PongApp** folder and change to that directory with e.g. `cd PongApp`. Then type:
```
    python -m PyInstaller --hidden-import="pkg_resources.py2_warn" --name pong example\path\to\main.py
```
3. The spec file will be **pong.spec** located in **PongApp**. Now we need to edit the spec file to add the dependencies hooks to correctly build the exe. Open the spec file with your favorite editor and add these lines at the beginning of the spec (assuming sdl2 is used, the default now):
```
    from kivy_deps import sdl2, glew
```
Then, find `COLLECT()` and add the data for pong (pong.kv): Change the line to add a `Tree()` object, e.g. `Tree('example\\path\\to\\')`. This `Tree` will search and add every file found in the touchtracer directory to your final package.
To add the dependencies, before the first keyword argument in `COLLECT` add a `Tree` object for every path of the dependencies. E.g. `*[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)]` so it’ll look something like:
```
    coll = COLLECT(exe, Tree('example\\path\\to\\'),
                   a.binaries,
                   a.zipfiles,
                   a.datas,
                   *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
                   strip=False,
                   upx=True,
                   upx_exclude=[],
                   name='pong')
```
4. Now we build the spec file in **PongApp** with:
```
    python -m PyInstaller pong.spec
```
5. The compiled package will be in the *PongApp\dist\pong* directory.
