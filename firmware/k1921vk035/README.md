# Сборка

Требуется:

* CMake 3.8+
* make

Например, сборка прошивки под К1921ВК035:

```bash
mkdir build-release && cd build-release
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build .
```

# Прошивка загрузчика

Требуется:

* openocd

```bash
cd init
# Разрешаем работу загрузчика
openocd -f enable_boot.cfg
# Выполняем сброс по питанию или по кнопке, затем зашиваем загрузчик с помощью
openocd -f program_boot.cfg
```
