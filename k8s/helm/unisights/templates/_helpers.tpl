{{- define "unisights.fullname" -}}
unisights
{{- end -}}

{{- define "unisights.labels" -}}
app.kubernetes.io/part-of: unisights
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "unisights.componentLabels" -}}
{{- $component := . -}}
app.kubernetes.io/name: {{ $component }}
app.kubernetes.io/instance: {{ $component }}
{{- end -}}

{{- define "unisights.secretName" -}}
{{- .Values.secrets.existingSecret | default "unisights-secrets" -}}
{{- end -}}
