# Конфигурация

Прошивка конфигурируется с помощью дефайнов, заданных в скрипте ```CMakeLists.txt```

Частота внешнего генератора или кварцевого осциллятора может принимать значения: 8000000, 12000000, 16000000, 20000000, 24000000
```
ADD_DEFINITIONS(-DXIOSC=12000000)
```

Буква порта для вывода BOOTEN может принимать значения: A, B, C, D, E, F, G, H
```
ADD_DEFINITIONS(-DBOOTEN_PORT_LETTER=E)
```

Номер пина для вывода BOOTEN может принимать значения: 0 - 15
```
ADD_DEFINITIONS(-DBOOTEN_PIN_NUMBER=8)
```

Номер UART может принимать значения: 0 - 3
```
ADD_DEFINITIONS(-DUART_NUMBER=2)
```

# Сборка

Требуется:

* CMake 3.8+
* make

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
