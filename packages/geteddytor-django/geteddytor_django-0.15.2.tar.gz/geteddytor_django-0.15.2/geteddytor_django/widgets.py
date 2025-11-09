from django import forms
from django.utils.safestring import mark_safe
import json

class EddytorWidget(forms.Widget):
    template_name = 'eddytor/widget.html'

    class Media:
        css = {'all': ('eddytor/eddytor.css',)}
        js = ('eddytor/eddytor.js',)

    def __init__(self, attrs=None, config=None, **kwargs):
        self.config = config or {}
        default_attrs = {'class': 'eddytor'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['config'] = self.config
        context['widget']['value'] = value
        return context

    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        config_json = json.dumps(self.config)
        editor_id = f"eddytor-{name}"

        INIT = f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            let cfg = {config_json};

            // ---- AI Rewrite dynamic transform binding ----
            if(cfg.aiRewrite && cfg.aiRewrite.enabled) {{
                const raw = cfg.aiRewrite.requestTransform || {{}};

                // If requestTransform is an object (not a function), convert it
                if(typeof raw === 'object' && !Array.isArray(raw)) {{
                    cfg.aiRewrite.requestTransform = (content) => {{
                        const payload = {{ text: content }};
                        Object.entries(raw).forEach(([k,v]) => {{
                            payload[k] = v;
                        }});
                        return payload;
                    }};
                }}

                // optional transform
                if(cfg.aiRewrite.responseTransform === true) {{
                    cfg.aiRewrite.responseTransform = (res) => res.rewritten_text;
                }}
            }}

            // ---- Azure DevOps dynamic transform binding ----
            if(cfg.azureDevOps && cfg.azureDevOps.enabled) {{
                const azureConfig = cfg.azureDevOps.buildQueryImportRequest || {{}};
                
                // Build the request function
                if(typeof azureConfig === 'object' && !Array.isArray(azureConfig)) {{
                    cfg.azureDevOps.buildQueryImportRequest = (queryUrl) => {{
                        const request = {{
                            method: azureConfig.method || 'POST',
                            headers: azureConfig.headers || {{ 'Content-Type': 'application/json' }}
                        }};
                        
                        // Build body based on bodyField
                        if(azureConfig.bodyField) {{
                            const bodyObj = {{}};
                            bodyObj[azureConfig.bodyField] = queryUrl;
                            request.body = JSON.stringify(bodyObj);
                        }} else {{
                            request.body = JSON.stringify({{ queryUrl: queryUrl }});
                        }}
                        
                        return request;
                    }};
                }}

                // Response transform
                if(cfg.azureDevOps.queryImportResponseTransform === true) {{
                    cfg.azureDevOps.queryImportResponseTransform = (data) => ({{
                        html: data?.html ?? ''
                    }});
                }}
            }}

            // ---- Confluence dynamic transform binding ----
            if(cfg.confluence && cfg.confluence.enabled) {{
                const confluenceConfig = cfg.confluence.buildImportRequest || {{}};
                
                // Build the request function
                if(typeof confluenceConfig === 'object' && !Array.isArray(confluenceConfig)) {{
                    cfg.confluence.buildImportRequest = (pageUrl) => {{
                        const request = {{
                            method: confluenceConfig.method || 'POST',
                            headers: confluenceConfig.headers || {{ 'Content-Type': 'application/json' }}
                        }};
                        
                        // Build body based on bodyField
                        if(confluenceConfig.bodyField) {{
                            const bodyObj = {{}};
                            bodyObj[confluenceConfig.bodyField] = pageUrl;
                            request.body = JSON.stringify(bodyObj);
                        }} else {{
                            request.body = JSON.stringify({{ pageUrl: pageUrl }});
                        }}
                        
                        return request;
                    }};
                }}

                // Response transform
                if(cfg.confluence.importResponseTransform === true) {{
                    cfg.confluence.importResponseTransform = (data) => ({{
                        html: data?.html ?? '',
                        fileName: data?.title ?? ''
                    }});
                }}
            }}

            Eddytor.init("#{editor_id}", cfg);
        }});
        </script>
        """

        return mark_safe(html + INIT)