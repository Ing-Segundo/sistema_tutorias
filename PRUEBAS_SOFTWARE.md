# Documentación de Pruebas de Software — Sistema de Tutorías

Este documento detalla la metodología y ejecución de las pruebas de software realizadas sobre el sistema de tutorías académicas de la **UTN**, evaluando la aplicación mediante dos enfoques complementarios: **Pruebas de Caja Negra** y **Pruebas de Caja Blanca**.

Las pruebas automatizadas se encuentran implementadas en el archivo `test_app.py` utilizando el framework `pytest`.

* **Archivo de pruebas:** `test_app.py`
* **Total de pruebas:** 8 (4 de caja negra y 4 de caja blanca)
* **Comando de ejecución:** 
  ```bash
  pytest test_app.py -v
