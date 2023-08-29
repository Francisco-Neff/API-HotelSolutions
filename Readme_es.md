# HOTEL SOLUTIONS   
-----
API para la administración de habitaciones y reservas de un hotel.
-----

## Aplicaciones
- [Account](#account)

### Account
Lleva el registro de los diferentes usuarios de todo el proyecto en BBDD, como los diferentes métodos que esta aplicación pueda necesitar para trabajar con los registros.

## Despliegue

### Entorno de desarrollo
Actualiza el fichero `.env.template` con las variables de entorno necesarias.

Ejecuta el siguiente comando.
```bash
docker-compose --env-file .env.template up -d 
```