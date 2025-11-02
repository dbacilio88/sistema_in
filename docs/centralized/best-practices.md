# Guía de Mejores Prácticas - Sistema de Detección de Infracciones

## Introducción

Esta guía compila las mejores prácticas para el desarrollo, operación y mantenimiento del Sistema de Detección de Infracciones de Tráfico. Las prácticas están organizadas por área funcional y nivel de experiencia.

## 🏗️ Desarrollo de Software

### Estándares de Código

#### Python (Backend Django)

**Estructura de Archivos:**
```python
# ✅ Bueno: Importaciones organizadas
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

import requests
from django.db import models
from django.core.exceptions import ValidationError

from authentication.models import User
from vehicles.models import Vehicle

# ❌ Malo: Importaciones desordenadas
from datetime import datetime
from django.db import models
import requests
from authentication.models import User
from typing import List
```

**Documentación de Funciones:**
```python
# ✅ Bueno: Documentación completa
def detect_license_plate(image_path: str, confidence_threshold: float = 0.8) -> Dict[str, Any]:
    """
    Detecta placas vehiculares en una imagen usando ML.
    
    Args:
        image_path: Ruta absoluta a la imagen a procesar
        confidence_threshold: Umbral mínimo de confianza (0.0-1.0)
    
    Returns:
        Dict con 'plates' (lista de placas detectadas), 'confidence' y 'processing_time'
        
    Raises:
        FileNotFoundError: Si la imagen no existe
        ValidationError: Si confidence_threshold no está en rango válido
        
    Example:
        >>> result = detect_license_plate('/path/image.jpg', 0.9)
        >>> print(result['plates'])
        ['ABC123', 'XYZ789']
    """
    if not 0.0 <= confidence_threshold <= 1.0:
        raise ValidationError("Confidence threshold must be between 0.0 and 1.0")
    
    # Implementation here...
    return {
        'plates': detected_plates,
        'confidence': avg_confidence,
        'processing_time': elapsed_time
    }

# ❌ Malo: Sin documentación
def detect_license_plate(image_path, confidence_threshold=0.8):
    # Implementation without documentation
    pass
```

**Manejo de Errores:**
```python
# ✅ Bueno: Manejo específico de errores
from infractions.exceptions import ProcessingError, InsufficientConfidenceError

def process_infraction(image_data: bytes) -> Infraction:
    try:
        plates = detect_plates(image_data)
        if not plates:
            raise InsufficientConfidenceError("No plates detected with sufficient confidence")
            
        vehicle = Vehicle.objects.get(license_plate=plates[0])
        return create_infraction(vehicle, image_data)
        
    except Vehicle.DoesNotExist:
        logger.warning(f"Vehicle with plate {plates[0]} not found")
        raise ProcessingError(f"Vehicle {plates[0]} not registered")
    except Exception as e:
        logger.error(f"Unexpected error processing infraction: {e}")
        raise ProcessingError("Failed to process infraction")

# ❌ Malo: Manejo genérico
def process_infraction(image_data):
    try:
        # Complex logic here
        pass
    except Exception as e:
        print(f"Error: {e}")  # Nunca usar print en producción
        return None
```

#### JavaScript/TypeScript (Frontend React)

**Componentes Funcionales:**
```typescript
// ✅ Bueno: Componente bien estructurado
import React, { useState, useEffect, useCallback } from 'react';
import { Infraction, ApiResponse } from '../types';
import { infractions } from '../services/api';
import { LoadingSpinner, ErrorMessage } from '../components/common';

interface InfractionListProps {
  vehicleId?: string;
  limit?: number;
  onInfractionSelect?: (infraction: Infraction) => void;
}

export const InfractionList: React.FC<InfractionListProps> = ({
  vehicleId,
  limit = 10,
  onInfractionSelect
}) => {
  const [infractions, setInfractions] = useState<Infraction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInfractions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await infractions.list({ vehicleId, limit });
      setInfractions(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch infractions');
    } finally {
      setLoading(false);
    }
  }, [vehicleId, limit]);

  useEffect(() => {
    fetchInfractions();
  }, [fetchInfractions]);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} onRetry={fetchInfractions} />;

  return (
    <div className="infraction-list">
      {infractions.map(infraction => (
        <InfractionCard
          key={infraction.id}
          infraction={infraction}
          onClick={() => onInfractionSelect?.(infraction)}
        />
      ))}
    </div>
  );
};

// ❌ Malo: Componente sin tipado y mal estructurado
export const InfractionList = ({ vehicleId, limit, onInfractionSelect }) => {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    fetch(`/api/infractions?vehicle=${vehicleId}&limit=${limit}`)
      .then(res => res.json())
      .then(data => setData(data))
      .catch(err => console.log(err));
  }, []);

  return (
    <div>
      {data.map(item => <div key={item.id}>{item.description}</div>)}
    </div>
  );
};
```

### Testing

#### Backend Testing (Django)

**Pruebas Unitarias:**
```python
# ✅ Bueno: Pruebas completas y organizadas
import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.exceptions import ValidationError

from infractions.models import Infraction
from infractions.services import InfractionProcessor
from infractions.exceptions import ProcessingError

class TestInfractionProcessor(TestCase):
    def setUp(self):
        self.processor = InfractionProcessor()
        self.sample_image_data = b'fake_image_data'
    
    @patch('infractions.services.detect_plates')
    def test_process_infraction_success(self, mock_detect):
        """Test successful infraction processing"""
        # Arrange
        mock_detect.return_value = ['ABC123']
        vehicle = self.create_test_vehicle('ABC123')
        
        # Act
        infraction = self.processor.process(self.sample_image_data)
        
        # Assert
        self.assertIsInstance(infraction, Infraction)
        self.assertEqual(infraction.vehicle, vehicle)
        mock_detect.assert_called_once_with(self.sample_image_data)
    
    @patch('infractions.services.detect_plates')
    def test_process_infraction_no_plates_detected(self, mock_detect):
        """Test processing when no plates are detected"""
        # Arrange
        mock_detect.return_value = []
        
        # Act & Assert
        with self.assertRaises(ProcessingError) as context:
            self.processor.process(self.sample_image_data)
        
        self.assertIn("No plates detected", str(context.exception))
    
    def create_test_vehicle(self, license_plate):
        """Helper method to create test vehicle"""
        from vehicles.models import Vehicle
        return Vehicle.objects.create(
            license_plate=license_plate,
            owner_name="Test Owner",
            model="Test Model"
        )

# ❌ Malo: Pruebas incompletas
class TestInfractionProcessor:
    def test_process(self):
        processor = InfractionProcessor()
        result = processor.process(b'data')
        assert result is not None  # Muy genérico
```

**Pruebas de Integración:**
```python
# ✅ Bueno: Pruebas de API completas
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class InfractionAPITest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='administrator'
        )
        self.operator_user = User.objects.create_user(
            username='operator',
            email='operator@test.com', 
            password='testpass123',
            role='operator'
        )
    
    def test_list_infractions_as_admin(self):
        """Admin can view all infractions"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/infractions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_list_infractions_as_operator(self):
        """Operator can view infractions"""
        self.client.force_authenticate(user=self.operator_user)
        response = self.client.get('/api/v1/infractions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_infractions_unauthorized(self):
        """Unauthorized access should be rejected"""
        response = self.client.get('/api/v1/infractions/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

#### Frontend Testing (React)

**Pruebas de Componentes:**
```typescript
// ✅ Bueno: Pruebas completas con Testing Library
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { InfractionList } from '../InfractionList';
import { Infraction } from '../../types';

const mockInfractions: Infraction[] = [
  {
    id: '1',
    vehicleId: 'vehicle-1',
    description: 'Speeding violation',
    timestamp: '2024-01-01T10:00:00Z',
    location: 'Main St & 1st Ave'
  }
];

const server = setupServer(
  rest.get('/api/v1/infractions/', (req, res, ctx) => {
    return res(ctx.json({ results: mockInfractions }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('InfractionList', () => {
  test('renders infractions successfully', async () => {
    render(<InfractionList />);
    
    // Verify loading state
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Speeding violation')).toBeInTheDocument();
    });
    
    // Verify content
    expect(screen.getByText('Main St & 1st Ave')).toBeInTheDocument();
  });
  
  test('handles API error gracefully', async () => {
    server.use(
      rest.get('/api/v1/infractions/', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Server error' }));
      })
    );
    
    render(<InfractionList />);
    
    await waitFor(() => {
      expect(screen.getByText(/Failed to fetch infractions/)).toBeInTheDocument();
    });
    
    // Test retry functionality
    const retryButton = screen.getByText('Retry');
    fireEvent.click(retryButton);
    
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });
  
  test('calls onInfractionSelect when infraction is clicked', async () => {
    const mockOnSelect = jest.fn();
    render(<InfractionList onInfractionSelect={mockOnSelect} />);
    
    await waitFor(() => {
      expect(screen.getByText('Speeding violation')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('Speeding violation'));
    expect(mockOnSelect).toHaveBeenCalledWith(mockInfractions[0]);
  });
});

// ❌ Malo: Pruebas superficiales
describe('InfractionList', () => {
  test('renders', () => {
    render(<InfractionList />);
    expect(screen.getByText('Infractions')).toBeInTheDocument();
  });
});
```

---

## 🛠️ Operaciones DevOps

### Deployment

#### Continuous Integration

**GitHub Actions Workflow:**
```yaml
# ✅ Bueno: Pipeline completo con gates de calidad
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: traffic-system

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
        node-version: [18, 20]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache Python dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    
    - name: Install Python dependencies
      run: |
        pip install -r backend-django/requirements.txt
        pip install -r backend-django/requirements-dev.txt
    
    - name: Run Python linting
      run: |
        flake8 backend-django --count --select=E9,F63,F7,F82 --show-source --statistics
        black --check backend-django
        isort --check-only backend-django
    
    - name: Run Python tests
      run: |
        cd backend-django
        coverage run --source='.' manage.py test
        coverage report --fail-under=80
        coverage xml
    
    - name: Set up Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
        cache-dependency-path: frontend-react/package-lock.json
    
    - name: Install Node.js dependencies
      run: |
        cd frontend-react
        npm ci
    
    - name: Run Frontend linting
      run: |
        cd frontend-react
        npm run lint
        npm run type-check
    
    - name: Run Frontend tests
      run: |
        cd frontend-react
        npm run test -- --coverage --watchAll=false
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./backend-django/coverage.xml,./frontend-react/coverage/lcov.info

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Snyk security scan
      uses: snyk/actions/python@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      with:
        args: --severity-threshold=high
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  build-and-push:
    needs: [test, security]
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push Docker images
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./backend-django/Dockerfile
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Configure kubectl
      uses: azure/k8s-set-context@v3
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/traffic-system-backend \
          backend=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
          -n traffic-system
        
        kubectl rollout status deployment/traffic-system-backend -n traffic-system

# ❌ Malo: Pipeline básico sin validaciones
name: Simple Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - run: docker build -t app .
    - run: kubectl apply -f deployment.yaml
```

#### Infrastructure as Code

**Terraform Best Practices:**
```hcl
# ✅ Bueno: Código Terraform bien estructurado
# modules/eks-cluster/main.tf

locals {
  cluster_name = "${var.environment}-${var.project_name}-cluster"
  
  common_tags = {
    Environment   = var.environment
    Project      = var.project_name
    Owner        = var.owner
    ManagedBy    = "terraform"
    CreatedDate  = formatdate("YYYY-MM-DD", timestamp())
  }
}

data "aws_availability_zones" "available" {
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

resource "aws_eks_cluster" "main" {
  name     = local.cluster_name
  role_arn = aws_iam_role.eks_cluster.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids              = var.subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = var.enable_public_access
    public_access_cidrs    = var.public_access_cidrs
    
    security_group_ids = [aws_security_group.eks_cluster.id]
  }

  encryption_config {
    provider {
      key_arn = aws_kms_key.eks.arn
    }
    resources = ["secrets"]
  }

  enabled_cluster_log_types = [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler"
  ]

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_vpc_resource_controller,
    aws_cloudwatch_log_group.eks_cluster,
  ]

  tags = local.common_tags
}

# ❌ Malo: Código sin organización
resource "aws_eks_cluster" "cluster" {
  name     = "my-cluster"
  role_arn = "arn:aws:iam::123456789012:role/eks-role"
  
  vpc_config {
    subnet_ids = ["subnet-123", "subnet-456"]
  }
}
```

### Monitoring y Alerting

#### Prometheus Alerting Rules

**Alertas Bien Configuradas:**
```yaml
# ✅ Bueno: Alertas específicas y accionables
groups:
- name: traffic-system.rules
  interval: 30s
  rules:
  
  # Application Health
  - alert: TrafficSystemDown
    expr: up{job="traffic-system-backend"} == 0
    for: 1m
    labels:
      severity: critical
      service: traffic-system
      component: backend
    annotations:
      summary: "Traffic System backend is down"
      description: "Traffic System backend has been down for more than 1 minute. No traffic infractions can be processed."
      runbook_url: "https://runbooks.company.com/traffic-system-down"
      dashboard_url: "https://grafana.company.com/d/traffic-system"
  
  - alert: MLServiceHighLatency
    expr: histogram_quantile(0.95, rate(ml_inference_duration_seconds_bucket[5m])) > 5
    for: 3m
    labels:
      severity: warning
      service: traffic-system
      component: ml-service
    annotations:
      summary: "ML Service experiencing high latency"
      description: "95th percentile latency is {{ $value }}s, which is above the 5s threshold."
      impact: "License plate detection may be slower than expected"
      runbook_url: "https://runbooks.company.com/ml-service-latency"
  
  # Infrastructure
  - alert: DatabaseConnectionsHigh
    expr: pg_stat_database_numbackends{datname="trafficdb"} > 80
    for: 2m
    labels:
      severity: warning
      service: traffic-system
      component: database
    annotations:
      summary: "High number of database connections"
      description: "Database has {{ $value }} connections, approaching the limit of 100."
      action_required: "Consider scaling the database or investigating connection leaks"
  
  - alert: DiskSpaceRunningLow
    expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 15
    for: 5m
    labels:
      severity: warning
      service: infrastructure
      component: storage
    annotations:
      summary: "Disk space running low"
      description: "Disk space is {{ $value | humanize }}% full on {{ $labels.instance }}"
      action_required: "Clean up old files or expand disk capacity"

# ❌ Malo: Alertas genéricas sin contexto
groups:
- name: alerts
  rules:
  - alert: HighCPU
    expr: cpu > 80
    annotations:
      summary: "CPU is high"
  
  - alert: ServiceDown
    expr: up == 0
    annotations:
      summary: "Service is down"
```

---

## 🔒 Seguridad

### Autenticación y Autorización

#### JWT Best Practices

**Implementación Segura:**
```python
# ✅ Bueno: JWT con validaciones apropiadas
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256'],
                options={
                    'verify_exp': True,
                    'verify_iat': True,
                    'verify_signature': True,
                    'require_exp': True,
                    'require_iat': True,
                }
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        
        try:
            user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')
        
        if not user.is_active:
            raise AuthenticationFailed('User account is disabled')
        
        # Verify token hasn't been revoked
        if self.is_token_revoked(token):
            raise AuthenticationFailed('Token has been revoked')
        
        return (user, token)
    
    def is_token_revoked(self, token):
        """Check if token is in revocation list"""
        from django.core.cache import cache
        return cache.get(f'revoked_token_{token}') is not None

def create_token(user):
    """Create JWT token with proper claims"""
    now = datetime.utcnow()
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'iat': now,
        'exp': now + timedelta(hours=24),
        'jti': str(uuid.uuid4()),  # Unique token ID
        'iss': 'traffic-system',   # Issuer
        'aud': 'traffic-system',   # Audience
    }
    
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

# ❌ Malo: JWT sin validaciones
def authenticate(request):
    token = request.headers.get('Authorization')
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        return User.objects.get(id=payload['user_id'])
    except:
        return None
```

#### Permissions

**Sistema de Permisos Granular:**
```python
# ✅ Bueno: Permisos específicos y bien documentados
from rest_framework import permissions
from django.contrib.contenttypes.models import ContentType

class InfractionPermission(permissions.BasePermission):
    """
    Permisos para gestionar infracciones:
    - Administradores: Acceso completo
    - Operadores: Lectura y creación
    - Técnicos de campo: Solo lectura de sus asignaciones
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.role == 'administrator':
            return True
        
        if request.user.role == 'operator':
            return request.method in permissions.SAFE_METHODS or request.method == 'POST'
        
        if request.user.role == 'field_technician':
            return request.method in permissions.SAFE_METHODS
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'administrator':
            return True
        
        if request.user.role == 'operator':
            # Operadores pueden modificar infracciones no procesadas
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return obj.status == 'pending'
            return True
        
        if request.user.role == 'field_technician':
            # Técnicos solo ven infracciones asignadas
            return obj.assigned_technician == request.user
        
        return False

class ConfigurationPermission(permissions.BasePermission):
    """
    Solo administradores pueden modificar configuración del sistema
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        return (
            request.user.is_authenticated and 
            request.user.role == 'administrator'
        )

# ❌ Malo: Permisos demasiado amplios
class InfractionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated  # Muy permisivo
```

### Validación de Datos

#### Input Validation

**Validación Robusta:**
```python
# ✅ Bueno: Validación completa con sanitización
from rest_framework import serializers
from django.core.validators import RegexValidator
import bleach
from PIL import Image
import magic

class InfractionCreateSerializer(serializers.ModelSerializer):
    license_plate = serializers.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9]{3}-[A-Z0-9]{3}$',
                message='License plate must be in format ABC-123'
            )
        ]
    )
    
    location = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000)
    evidence_image = serializers.ImageField()
    
    def validate_license_plate(self, value):
        """Validate license plate format and existence"""
        value = value.upper().strip()
        
        # Check if vehicle exists
        from vehicles.models import Vehicle
        if not Vehicle.objects.filter(license_plate=value).exists():
            raise serializers.ValidationError(
                f"Vehicle with license plate {value} is not registered"
            )
        
        return value
    
    def validate_location(self, value):
        """Sanitize location string"""
        # Remove potential XSS
        cleaned = bleach.clean(value, tags=[], strip=True)
        
        if len(cleaned.strip()) < 5:
            raise serializers.ValidationError(
                "Location must be at least 5 characters long"
            )
        
        return cleaned.strip()
    
    def validate_evidence_image(self, value):
        """Validate uploaded image"""
        # Check file size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError(
                "Image file too large. Maximum size is 5MB"
            )
        
        # Verify it's actually an image
        try:
            img = Image.open(value)
            img.verify()
        except Exception:
            raise serializers.ValidationError("Invalid image file")
        
        # Check MIME type
        mime_type = magic.from_buffer(value.read(), mime=True)
        value.seek(0)  # Reset file pointer
        
        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        if mime_type not in allowed_types:
            raise serializers.ValidationError(
                f"Unsupported image type: {mime_type}"
            )
        
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        # Check if this infraction already exists
        from infractions.models import Infraction
        from datetime import datetime, timedelta
        
        recent_infractions = Infraction.objects.filter(
            license_plate=attrs['license_plate'],
            location=attrs['location'],
            created_at__gte=datetime.now() - timedelta(minutes=30)
        )
        
        if recent_infractions.exists():
            raise serializers.ValidationError(
                "A similar infraction was already reported recently"
            )
        
        return attrs

# ❌ Malo: Validación mínima
class InfractionCreateSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        if not attrs.get('license_plate'):
            raise serializers.ValidationError("License plate required")
        return attrs
```

---

## 📊 Performance

### Database Optimization

#### Query Optimization

**Queries Eficientes:**
```python
# ✅ Bueno: Queries optimizadas
from django.db import models
from django.db.models import Prefetch, Count, Q, F

class InfractionQuerySet(models.QuerySet):
    def with_vehicle_details(self):
        """Include vehicle information in a single query"""
        return self.select_related(
            'vehicle',
            'vehicle__owner',
            'assigned_technician'
        )
    
    def with_evidence_count(self):
        """Add evidence count without extra queries"""
        return self.annotate(
            evidence_count=Count('evidence_files')
        )
    
    def pending_for_technician(self, technician):
        """Get pending infractions for specific technician"""
        return self.filter(
            assigned_technician=technician,
            status='pending'
        ).order_by('created_at')
    
    def recent_by_location(self, location, days=30):
        """Get recent infractions in specific location"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return self.filter(
            location__icontains=location,
            created_at__gte=cutoff_date
        ).order_by('-created_at')

class InfractionManager(models.Manager):
    def get_queryset(self):
        return InfractionQuerySet(self.model, using=self._db)
    
    def dashboard_stats(self, user):
        """Optimized dashboard statistics"""
        queryset = self.get_queryset()
        
        if user.role == 'field_technician':
            queryset = queryset.filter(assigned_technician=user)
        
        # Single query for multiple aggregations
        stats = queryset.aggregate(
            total_count=Count('id'),
            pending_count=Count('id', filter=Q(status='pending')),
            processed_count=Count('id', filter=Q(status='processed')),
            today_count=Count('id', filter=Q(
                created_at__date=timezone.now().date()
            ))
        )
        
        return stats

# Usage in views
def infraction_list(request):
    infractions = Infraction.objects.with_vehicle_details().with_evidence_count()
    
    if request.user.role == 'field_technician':
        infractions = infractions.pending_for_technician(request.user)
    
    return render(request, 'infractions/list.html', {
        'infractions': infractions[:50]  # Limit results
    })

# ❌ Malo: N+1 queries
def infraction_list(request):
    infractions = Infraction.objects.all()
    
    for infraction in infractions:  # N+1 problem
        print(infraction.vehicle.license_plate)  # Extra query per infraction
        print(infraction.assigned_technician.name)  # Another extra query
```

#### Database Indexing

**Índices Estratégicos:**
```python
# ✅ Bueno: Índices bien planificados
from django.db import models

class Infraction(models.Model):
    license_plate = models.CharField(max_length=10, db_index=True)
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    assigned_technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        # Composite indexes for common query patterns
        indexes = [
            # For technician dashboard
            models.Index(fields=['assigned_technician', 'status', 'created_at']),
            # For location-based searches
            models.Index(fields=['location', 'created_at']),
            # For status filtering with date range
            models.Index(fields=['status', 'created_at']),
            # For license plate history
            models.Index(fields=['license_plate', '-created_at']),
        ]
        
        # Database constraints
        constraints = [
            models.CheckConstraint(
                check=Q(license_plate__regex=r'^[A-Z0-9]{3}-[A-Z0-9]{3}$'),
                name='valid_license_plate_format'
            )
        ]

# ❌ Malo: Sin índices o índices innecesarios
class Infraction(models.Model):
    license_plate = models.CharField(max_length=10)  # No index on frequently searched field
    description = models.TextField(db_index=True)    # Unnecessary index on large text field
```

### Caching

#### Redis Caching Strategy

**Estrategia de Cache Efectiva:**
```python
# ✅ Bueno: Cache estratégico y bien gestionado
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
import hashlib
import json
from functools import wraps

class CacheManager:
    # Cache TTL constants
    CACHE_TTL_SHORT = 300      # 5 minutes
    CACHE_TTL_MEDIUM = 1800    # 30 minutes  
    CACHE_TTL_LONG = 3600      # 1 hour
    CACHE_TTL_VERY_LONG = 86400 # 24 hours

    @staticmethod
    def get_cache_key(prefix, *args, **kwargs):
        """Generate consistent cache keys"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

def cached_query(timeout=CacheManager.CACHE_TTL_MEDIUM, prefix='query'):
    """Decorator for caching expensive database queries"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = CacheManager.get_cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator

# Application-specific caching
class InfractionCacheService:
    @staticmethod
    @cached_query(timeout=CacheManager.CACHE_TTL_SHORT, prefix='infraction_stats')
    def get_dashboard_stats(user_id, user_role):
        """Cache dashboard statistics"""
        from infractions.models import Infraction
        
        queryset = Infraction.objects.all()
        if user_role == 'field_technician':
            queryset = queryset.filter(assigned_technician_id=user_id)
        
        return queryset.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            processed=Count('id', filter=Q(status='processed'))
        )
    
    @staticmethod
    @cached_query(timeout=CacheManager.CACHE_TTL_LONG, prefix='location_stats')
    def get_location_statistics():
        """Cache location-based statistics"""
        from django.db.models import Count
        from infractions.models import Infraction
        
        return list(
            Infraction.objects
            .values('location')
            .annotate(count=Count('id'))
            .order_by('-count')[:20]
        )
    
    @staticmethod
    def invalidate_user_cache(user_id):
        """Invalidate all cache entries for a user"""
        # Pattern-based cache invalidation
        cache_patterns = [
            f'infraction_stats:*{user_id}*',
            f'user_permissions:*{user_id}*'
        ]
        
        for pattern in cache_patterns:
            # Redis SCAN for pattern matching
            from django.core.cache import cache
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(pattern)

# Template fragment caching
# In templates:
# {% load cache %}
# {% cache 300 infraction_list user.id user.role %}
#   <!-- Expensive template rendering -->
# {% endcache %}

# ❌ Malo: Cache sin estrategia
def get_stats():
    result = cache.get('stats')
    if not result:
        result = expensive_calculation()
        cache.set('stats', result)  # No TTL, no invalidation strategy
    return result
```

---

## 🎨 Frontend Best Practices

### React Performance

#### Component Optimization

**Componentes Optimizados:**
```typescript
// ✅ Bueno: Componente optimizado con memoización
import React, { memo, useMemo, useCallback, useState } from 'react';
import { Infraction, SortOption } from '../types';

interface InfractionListProps {
  infractions: Infraction[];
  onInfractionSelect: (infraction: Infraction) => void;
  loading?: boolean;
}

// Memoized sub-component
const InfractionCard = memo<{
  infraction: Infraction;
  onClick: () => void;
}>(({ infraction, onClick }) => {
  const formattedDate = useMemo(() => 
    new Intl.DateTimeFormat('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(infraction.timestamp))
  , [infraction.timestamp]);

  return (
    <div 
      className="infraction-card"
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      <div className="infraction-header">
        <span className="license-plate">{infraction.licensePlate}</span>
        <span className={`status status-${infraction.status}`}>
          {infraction.status}
        </span>
      </div>
      <div className="infraction-details">
        <p className="location">{infraction.location}</p>
        <p className="timestamp">{formattedDate}</p>
      </div>
    </div>
  );
});

export const InfractionList: React.FC<InfractionListProps> = memo(({
  infractions,
  onInfractionSelect,
  loading = false
}) => {
  const [sortBy, setSortBy] = useState<SortOption>('timestamp');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  // Memoized filtered and sorted data
  const filteredInfractions = useMemo(() => {
    let filtered = infractions;
    
    if (filterStatus !== 'all') {
      filtered = filtered.filter(infraction => 
        infraction.status === filterStatus
      );
    }
    
    return filtered.sort((a, b) => {
      switch (sortBy) {
        case 'timestamp':
          return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
        case 'location':
          return a.location.localeCompare(b.location);
        case 'status':
          return a.status.localeCompare(b.status);
        default:
          return 0;
      }
    });
  }, [infractions, filterStatus, sortBy]);

  // Memoized event handlers
  const handleSortChange = useCallback((newSort: SortOption) => {
    setSortBy(newSort);
  }, []);

  const handleFilterChange = useCallback((status: string) => {
    setFilterStatus(status);
  }, []);

  const handleInfractionClick = useCallback((infraction: Infraction) => {
    onInfractionSelect(infraction);
  }, [onInfractionSelect]);

  if (loading) {
    return <LoadingSkeleton count={5} />;
  }

  return (
    <div className="infraction-list">
      <div className="controls">
        <SortControl value={sortBy} onChange={handleSortChange} />
        <FilterControl value={filterStatus} onChange={handleFilterChange} />
      </div>
      
      <div className="list-container">
        {filteredInfractions.map(infraction => (
          <InfractionCard
            key={infraction.id}
            infraction={infraction}
            onClick={() => handleInfractionClick(infraction)}
          />
        ))}
      </div>
    </div>
  );
});

// ❌ Malo: Componente sin optimización
export const InfractionList = ({ infractions, onInfractionSelect }) => {
  const [sortBy, setSortBy] = useState('timestamp');
  
  // Re-creates on every render
  const sortedInfractions = infractions.sort((a, b) => {
    return new Date(b.timestamp) - new Date(a.timestamp);
  });

  return (
    <div>
      {sortedInfractions.map(infraction => (
        <div key={infraction.id} onClick={() => onInfractionSelect(infraction)}>
          {/* Inline formatting - no memoization */}
          <span>{new Date(infraction.timestamp).toLocaleDateString()}</span>
          <span>{infraction.licensePlate}</span>
        </div>
      ))}
    </div>
  );
};
```

#### State Management

**Redux Toolkit con Performance:**
```typescript
// ✅ Bueno: Estado bien estructurado con selectors
import { createSlice, createSelector, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../store';

interface InfractionsState {
  items: Record<string, Infraction>;
  ids: string[];
  loading: boolean;
  error: string | null;
  filters: {
    status: string;
    location: string;
    dateRange: {
      start: string | null;
      end: string | null;
    };
  };
  pagination: {
    page: number;
    limit: number;
    total: number;
  };
}

const initialState: InfractionsState = {
  items: {},
  ids: [],
  loading: false,
  error: null,
  filters: {
    status: 'all',
    location: '',
    dateRange: { start: null, end: null }
  },
  pagination: {
    page: 1,
    limit: 20,
    total: 0
  }
};

const infractionsSlice = createSlice({
  name: 'infractions',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    
    setInfractions: (state, action: PayloadAction<{
      infractions: Infraction[];
      total: number;
      page: number;
    }>) => {
      const { infractions, total, page } = action.payload;
      
      // Normalize data structure
      const items: Record<string, Infraction> = {};
      const ids: string[] = [];
      
      infractions.forEach(infraction => {
        items[infraction.id] = infraction;
        ids.push(infraction.id);
      });
      
      state.items = page === 1 ? items : { ...state.items, ...items };
      state.ids = page === 1 ? ids : [...state.ids, ...ids];
      state.pagination.total = total;
      state.pagination.page = page;
      state.loading = false;
    },
    
    updateInfraction: (state, action: PayloadAction<Infraction>) => {
      const infraction = action.payload;
      state.items[infraction.id] = infraction;
    },
    
    setFilters: (state, action: PayloadAction<Partial<InfractionsState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload };
      // Reset pagination when filters change
      state.pagination.page = 1;
    }
  }
});

// Memoized selectors for performance
export const selectInfractionsState = (state: RootState) => state.infractions;

export const selectAllInfractions = createSelector(
  [selectInfractionsState],
  (infractionsState) => 
    infractionsState.ids.map(id => infractionsState.items[id])
);

export const selectFilteredInfractions = createSelector(
  [selectAllInfractions, selectInfractionsState],
  (infractions, { filters }) => {
    return infractions.filter(infraction => {
      // Status filter
      if (filters.status !== 'all' && infraction.status !== filters.status) {
        return false;
      }
      
      // Location filter
      if (filters.location && !infraction.location.toLowerCase().includes(filters.location.toLowerCase())) {
        return false;
      }
      
      // Date range filter
      if (filters.dateRange.start || filters.dateRange.end) {
        const infractionDate = new Date(infraction.timestamp);
        
        if (filters.dateRange.start && infractionDate < new Date(filters.dateRange.start)) {
          return false;
        }
        
        if (filters.dateRange.end && infractionDate > new Date(filters.dateRange.end)) {
          return false;
        }
      }
      
      return true;
    });
  }
);

export const selectInfractionById = createSelector(
  [selectInfractionsState, (state: RootState, id: string) => id],
  (infractionsState, id) => infractionsState.items[id]
);

export const selectInfractionStats = createSelector(
  [selectFilteredInfractions],
  (infractions) => ({
    total: infractions.length,
    pending: infractions.filter(i => i.status === 'pending').length,
    processed: infractions.filter(i => i.status === 'processed').length,
    rejected: infractions.filter(i => i.status === 'rejected').length
  })
);

// ❌ Malo: Estado no normalizado
interface BadInfractionsState {
  infractions: Infraction[];  // Array makes updates expensive
  loading: boolean;
}

// Bad selector - no memoization
export const selectFilteredInfractions = (state: RootState) => 
  state.infractions.infractions.filter(i => i.status === 'pending');  // Runs on every render
```

---

## 📚 Documentación

### API Documentation

#### OpenAPI/Swagger

**Documentación Completa:**
```python
# ✅ Bueno: Documentación detallada con ejemplos
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

class InfractionViewSet(viewsets.ModelViewSet):
    queryset = Infraction.objects.all()
    serializer_class = InfractionSerializer
    
    @extend_schema(
        summary="List traffic infractions",
        description="""
        Retrieve a paginated list of traffic infractions.
        
        **Filtering Options:**
        - `status`: Filter by infraction status (pending, processed, rejected)
        - `license_plate`: Filter by exact license plate match
        - `location`: Filter by location (partial match supported)
        - `date_from` / `date_to`: Filter by date range
        
        **Permissions:**
        - Administrators: Can view all infractions
        - Operators: Can view all infractions
        - Field Technicians: Can only view assigned infractions
        """,
        parameters=[
            OpenApiParameter(
                name='status',
                description='Filter by infraction status',
                required=False,
                type=OpenApiTypes.STR,
                enum=['pending', 'processed', 'rejected']
            ),
            OpenApiParameter(
                name='license_plate',
                description='Exact license plate match (format: ABC-123)',
                required=False,
                type=OpenApiTypes.STR,
                pattern=r'^[A-Z0-9]{3}-[A-Z0-9]{3}$'
            ),
            OpenApiParameter(
                name='date_from',
                description='Start date for filtering (YYYY-MM-DD)',
                required=False,
                type=OpenApiTypes.DATE
            ),
            OpenApiParameter(
                name='date_to', 
                description='End date for filtering (YYYY-MM-DD)',
                required=False,
                type=OpenApiTypes.DATE
            )
        ],
        examples=[
            OpenApiExample(
                'List all pending infractions',
                value={'status': 'pending'},
                request_only=True
            ),
            OpenApiExample(
                'Filter by license plate',
                value={'license_plate': 'ABC-123'},
                request_only=True
            )
        ],
        responses={
            200: OpenApiExample(
                'Successful response',
                value={
                    "count": 150,
                    "next": "http://api.example.com/infractions/?page=2",
                    "previous": null,
                    "results": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "license_plate": "ABC-123",
                            "location": "Main St & 1st Ave",
                            "description": "Speeding violation - 45 mph in 30 mph zone",
                            "status": "pending",
                            "timestamp": "2024-01-15T10:30:00Z",
                            "evidence_url": "https://evidence.example.com/image123.jpg",
                            "assigned_technician": {
                                "id": "456",
                                "name": "John Doe",
                                "email": "john@example.com"
                            }
                        }
                    ]
                }
            )
        },
        tags=['Infractions']
    )
    def list(self, request):
        return super().list(request)
    
    @extend_schema(
        summary="Create new infraction",
        description="""
        Create a new traffic infraction record.
        
        **Required Fields:**
        - `license_plate`: Must be registered in the system
        - `location`: Intersection or address where violation occurred
        - `evidence_image`: Photo evidence (JPEG/PNG, max 5MB)
        
        **Automatic Processing:**
        - ML service will validate license plate detection
        - Geolocation will be verified if coordinates provided
        - Duplicate detection runs automatically
        """,
        examples=[
            OpenApiExample(
                'Create speeding infraction',
                value={
                    "license_plate": "XYZ-789",
                    "location": "Highway 101 Mile Marker 45",
                    "description": "Speed camera detection - 65 mph in 55 mph zone",
                    "violation_type": "speeding",
                    "coordinates": {
                        "latitude": 40.7128,
                        "longitude": -74.0060
                    }
                }
            )
        ],
        responses={
            201: 'Infraction created successfully',
            400: 'Invalid data provided',
            409: 'Duplicate infraction detected'
        }
    )
    def create(self, request):
        return super().create(request)

# ❌ Malo: Sin documentación detallada
class InfractionViewSet(viewsets.ModelViewSet):
    """Basic infraction CRUD"""  # Documentación mínima
    queryset = Infraction.objects.all()
    serializer_class = InfractionSerializer
```

### Code Comments

**Comentarios Efectivos:**
```python
# ✅ Bueno: Comentarios que explican el "por qué"
class LicensePlateDetector:
    def __init__(self, model_path: str, confidence_threshold: float = 0.8):
        """
        Initialize the license plate detector.
        
        Args:
            model_path: Path to the trained YOLO model
            confidence_threshold: Minimum confidence for valid detection
                Set to 0.8 based on validation testing to balance
                precision (95%) vs recall (87%)
        """
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        
        # Precompile regex for license plate validation
        # Colombian format: ABC-123 or ABC123
        self.plate_pattern = re.compile(r'^[A-Z]{3}-?[0-9]{3}$')
        
    def detect(self, image: np.ndarray) -> List[DetectedPlate]:
        """
        Detect license plates in the given image.
        
        Performance considerations:
        - Uses GPU acceleration if available (2x faster)
        - Image is resized to 640x640 for optimal inference speed
        - Non-max suppression removes duplicate detections
        """
        # Resize image for optimal model performance
        # Model was trained on 640x640 images
        resized_image = cv2.resize(image, (640, 640))
        
        results = self.model(resized_image)
        
        detected_plates = []
        for result in results:
            # Filter by confidence threshold
            # Lower threshold increases false positives significantly
            if result.confidence < self.confidence_threshold:
                continue
                
            # Extract text using OCR
            plate_text = self._extract_text(result.crop)
            
            # Validate format - reject if doesn't match Colombian plates
            if not self.plate_pattern.match(plate_text):
                continue
                
            detected_plates.append(DetectedPlate(
                text=plate_text,
                confidence=result.confidence,
                bbox=result.bbox
            ))
        
        return detected_plates
    
    def _extract_text(self, plate_image: np.ndarray) -> str:
        """
        Extract text from license plate image using OCR.
        
        Preprocessing steps are critical for accuracy:
        1. Convert to grayscale - reduces noise
        2. Apply Gaussian blur - smooths edges
        3. Apply threshold - creates binary image
        4. Morphological operations - connects broken characters
        """
        # Convert to grayscale
        gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        # Kernel size of 5x5 works best for typical license plate resolution
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Binary threshold
        # Value of 127 chosen through empirical testing
        _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
        
        # Use Tesseract with specific config for license plates
        # --psm 8: Single word mode (best for license plates)
        # -c tessedit_char_whitelist: Limit to alphanumeric characters
        custom_config = r'--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        text = pytesseract.image_to_string(thresh, config=custom_config)
        
        return text.strip().upper()

# ❌ Malo: Comentarios que solo repiten el código
class LicensePlateDetector:
    def detect(self, image):
        # Resize the image
        resized = cv2.resize(image, (640, 640))
        
        # Run the model
        results = self.model(resized)
        
        # Loop through results
        for result in results:
            # Check confidence
            if result.confidence > 0.8:
                # Extract text
                text = self.extract_text(result.crop)
```

---

**Resumen de Principios Clave:**

1. **Código Limpio**: Priorizar legibilidad y mantenibilidad
2. **Testing Comprensivo**: Cobertura alta con pruebas significativas
3. **Seguridad Primero**: Validación, sanitización y autenticación robusta
4. **Performance Consciente**: Optimización proactiva sin sacrificar claridad
5. **Documentación Viva**: Mantener documentación actualizada y útil
6. **Monitoreo Proactivo**: Observabilidad para detectar problemas temprano
7. **Automatización**: CI/CD y herramientas para reducir errores humanos
8. **Escalabilidad**: Diseñar para crecimiento desde el inicio