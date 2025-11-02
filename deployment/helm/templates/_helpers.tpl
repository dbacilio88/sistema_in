{{/*
Expand the name of the chart.
*/}}
{{- define "traffic-system.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "traffic-system.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "traffic-system.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "traffic-system.labels" -}}
helm.sh/chart: {{ include "traffic-system.chart" . }}
{{ include "traffic-system.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "traffic-system.selectorLabels" -}}
app.kubernetes.io/name: {{ include "traffic-system.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "traffic-system.serviceAccountName" -}}
{{- if .Values.security.serviceAccount.create }}
{{- default (include "traffic-system.fullname" .) .Values.security.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.security.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Backend labels
*/}}
{{- define "traffic-system.backend.labels" -}}
{{ include "traffic-system.labels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "traffic-system.backend.selectorLabels" -}}
{{ include "traffic-system.selectorLabels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
ML Service labels
*/}}
{{- define "traffic-system.mlservice.labels" -}}
{{ include "traffic-system.labels" . }}
app.kubernetes.io/component: ml-service
{{- end }}

{{/*
ML Service selector labels
*/}}
{{- define "traffic-system.mlservice.selectorLabels" -}}
{{ include "traffic-system.selectorLabels" . }}
app.kubernetes.io/component: ml-service
{{- end }}

{{/*
Config Service labels
*/}}
{{- define "traffic-system.configservice.labels" -}}
{{ include "traffic-system.labels" . }}
app.kubernetes.io/component: config-service
{{- end }}

{{/*
Config Service selector labels
*/}}
{{- define "traffic-system.configservice.selectorLabels" -}}
{{ include "traffic-system.selectorLabels" . }}
app.kubernetes.io/component: config-service
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "traffic-system.frontend.labels" -}}
{{ include "traffic-system.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "traffic-system.frontend.selectorLabels" -}}
{{ include "traffic-system.selectorLabels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Celery Worker labels
*/}}
{{- define "traffic-system.celery-worker.labels" -}}
{{ include "traffic-system.labels" . }}
app.kubernetes.io/component: celery-worker
{{- end }}

{{/*
Celery Worker selector labels
*/}}
{{- define "traffic-system.celery-worker.selectorLabels" -}}
{{ include "traffic-system.selectorLabels" . }}
app.kubernetes.io/component: celery-worker
{{- end }}

{{/*
Celery Beat labels
*/}}
{{- define "traffic-system.celery-beat.labels" -}}
{{ include "traffic-system.labels" . }}
app.kubernetes.io/component: celery-beat
{{- end }}

{{/*
Celery Beat selector labels
*/}}
{{- define "traffic-system.celery-beat.selectorLabels" -}}
{{ include "traffic-system.selectorLabels" . }}
app.kubernetes.io/component: celery-beat
{{- end }}

{{/*
Database URL
*/}}
{{- define "traffic-system.databaseUrl" -}}
{{- if .Values.postgresql.enabled }}
postgresql://{{ .Values.postgresql.auth.username }}:{{ .Values.postgresql.auth.password }}@{{ include "traffic-system.fullname" . }}-postgresql:5432/{{ .Values.postgresql.auth.database }}
{{- else }}
{{- .Values.backend.env.DATABASE_URL }}
{{- end }}
{{- end }}

{{/*
Redis URL
*/}}
{{- define "traffic-system.redisUrl" -}}
{{- if .Values.redis.enabled }}
{{- if .Values.redis.auth.enabled }}
redis://:{{ .Values.redis.auth.password }}@{{ include "traffic-system.fullname" . }}-redis-master:6379/0
{{- else }}
redis://{{ include "traffic-system.fullname" . }}-redis-master:6379/0
{{- end }}
{{- else }}
{{- .Values.backend.env.REDIS_URL }}
{{- end }}
{{- end }}

{{/*
Celery Broker URL
*/}}
{{- define "traffic-system.celeryBrokerUrl" -}}
{{- if .Values.rabbitmq.enabled }}
amqp://{{ .Values.rabbitmq.auth.username }}:{{ .Values.rabbitmq.auth.password }}@{{ include "traffic-system.fullname" . }}-rabbitmq:5672//
{{- else }}
{{- .Values.backend.env.CELERY_BROKER_URL }}
{{- end }}
{{- end }}

{{/*
MinIO URL
*/}}
{{- define "traffic-system.minioUrl" -}}
{{- if .Values.minio.enabled }}
http://{{ .Values.minio.auth.rootUser }}:{{ .Values.minio.auth.rootPassword }}@{{ include "traffic-system.fullname" . }}-minio:9000
{{- end }}
{{- end }}

{{/*
Common environment variables
*/}}
{{- define "traffic-system.commonEnv" -}}
- name: DATABASE_URL
  value: {{ include "traffic-system.databaseUrl" . | quote }}
- name: REDIS_URL
  value: {{ include "traffic-system.redisUrl" . | quote }}
- name: CELERY_BROKER_URL
  value: {{ include "traffic-system.celeryBrokerUrl" . | quote }}
{{- if .Values.minio.enabled }}
- name: MINIO_URL
  value: {{ include "traffic-system.minioUrl" . | quote }}
{{- end }}
- name: TZ
  value: {{ .Values.env.TZ | quote }}
- name: LOG_LEVEL
  value: {{ .Values.env.LOG_LEVEL | quote }}
- name: ENABLE_DEBUG_LOGS
  value: {{ .Values.env.ENABLE_DEBUG_LOGS | quote }}
- name: ENABLE_METRICS
  value: {{ .Values.env.ENABLE_METRICS | quote }}
{{- end }}

{{/*
Image pull policy
*/}}
{{- define "traffic-system.imagePullPolicy" -}}
{{- if .Values.global.imageRegistry }}
Always
{{- else }}
IfNotPresent
{{- end }}
{{- end }}

{{/*
Storage class
*/}}
{{- define "traffic-system.storageClass" -}}
{{- if .Values.global.storageClass }}
{{- .Values.global.storageClass }}
{{- else if .Values.persistence.storageClass }}
{{- .Values.persistence.storageClass }}
{{- end }}
{{- end }}