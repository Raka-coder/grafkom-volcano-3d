#version 330 core

in vec3 FragPos;
in vec3 Normal;
in vec3 Color;

out vec4 FragColor;

uniform vec3 cam_pos;
uniform sampler2D shadow_map;
uniform mat4 light_space;
uniform bool shadows_enabled = false;

float shadow_factor(vec3 world_pos, vec3 normal) {
    if (!shadows_enabled) return 1.0;

    vec4 proj = light_space * vec4(world_pos, 1.0);
    vec3 ndc = proj.xyz / proj.w;

    if (ndc.x < 0.0 || ndc.x > 1.0 || ndc.y < 0.0 || ndc.y > 1.0 || ndc.z < 0.0 || ndc.z > 1.0)
        return 1.0;

    float current = ndc.z;
    float bias = max(0.002, 0.002 * (1.0 - dot(normalize(normal), normalize(vec3(0.6, 1.0, 0.4)))));

    float shadow = 0.0;
    vec2 texel = 1.0 / textureSize(shadow_map, 0);
    for (int x = -1; x <= 1; x++) {
        for (int y = -1; y <= 1; y++) {
            float sample = texture(shadow_map, ndc.xy + vec2(x, y) * texel).r;
            shadow += current - bias > sample ? 1.0 : 0.0;
        }
    }
    return 1.0 - shadow / 9.0;
}

void main() {
    vec3 norm = normalize(Normal);
    vec3 view_dir = normalize(cam_pos - FragPos);
    vec3 sun_dir = normalize(vec3(0.6, 1.0, 0.4));
    vec3 sun_col = vec3(1.0, 0.95, 0.85);

    float diff = max(dot(norm, sun_dir), 0.0);
    vec3 halfway = normalize(sun_dir + view_dir);
    float spec = pow(max(dot(norm, halfway), 0.0), 16.0);

    float shad = shadow_factor(FragPos, Normal);
    vec3 ambient = 0.35 * sun_col;
    vec3 diffuse = 0.65 * diff * sun_col * shad;
    vec3 specular = spec * 0.15 * sun_col * shad;

    vec3 result = (ambient + diffuse) * Color + specular;
    FragColor = vec4(result, 1.0);
}
