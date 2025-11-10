# Configuración de Credenciales AWS para Terraform

## Opciones para Autenticación

### Opción 1: Variables de Entorno (Recomendado para CI/CD)
```bash
export AWS_ACCESS_KEY_ID="tu-access-key"
export AWS_SECRET_ACCESS_KEY="tu-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Opción 2: Variables en terraform.tfvars (No recomendado para producción)
```hcl
aws_access_key_id     = "AKIA..."
aws_secret_access_key = "tu-secret-key"
```

### Opción 3: Perfil AWS CLI (Recomendado para desarrollo local)
```bash
# Configurar perfil
aws configure

# O usar perfil específico
aws configure --profile sistema-in
export AWS_PROFILE=sistema-in
```

### Opción 4: IAM Roles (Recomendado para EC2/ECS)
Si ejecutas Terraform desde una instancia EC2 con un IAM Role, las credenciales se obtienen automáticamente.

## Configuración para GitHub Actions

En tu repositorio → Settings → Secrets and variables → Actions:

```
AWS_ACCESS_KEY_ID: tu_access_key
AWS_SECRET_ACCESS_KEY: tu_secret_key
AWS_KEY_PAIR_NAME: nombre-de-tu-key-pair (opcional)
```

## Permisos Necesarios

Tu usuario/role de AWS necesita estos permisos mínimos:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:*",
                "vpc:*",
                "iam:*",
                "logs:*",
                "ssm:*"
            ],
            "Resource": "*"
        }
    ]
}
```

## Orden de Precedencia de Credenciales

Terraform busca credenciales en este orden:

1. Variables en `terraform.tfvars` (aws_access_key_id, aws_secret_access_key)
2. Variables de entorno (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
3. Archivo de credenciales AWS CLI (~/.aws/credentials)
4. IAM Role (si está ejecutándose en EC2)

## Seguridad

⚠️ **Nunca commits credenciales en el código**

- Usa `.gitignore` para excluir `terraform.tfvars`
- Usa variables de entorno o AWS profiles
- Para producción, usa IAM Roles cuando sea posible