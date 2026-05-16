#version 330 core

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;

out vec4 FragColor;

uniform vec3 cam_pos;
uniform vec3 light_pos;
uniform float time;

uniform sampler2D tex_grass;
uniform sampler2D tex_rock;
uniform sampler2D tex_lava;

uniform vec3 fog_color = vec3(0.7, 0.8, 0.95);
uniform float fog_density = 0.003;

uniform sampler2D shadow_map;
uniform mat4 light_space;
uniform bool shadows_enabled = false;

uniform float ash_intensity = 0.0;
uniform float ash_radius = 60.0;

float shadow_factor(vec3 world_pos) {
    if (!shadows_enabled) return 1.0;

    vec4 proj = light_space * vec4(world_pos, 1.0);
    vec3 ndc = proj.xyz / proj.w;

    if (ndc.x < 0.0 || ndc.x > 1.0 || ndc.y < 0.0 || ndc.y > 1.0 || ndc.z < 0.0 || ndc.z > 1.0)
        return 1.0;

    float current = ndc.z;
    float bias = max(0.002, 0.002 * (1.0 - dot(normalize(Normal), normalize(vec3(0.6, 1.0, 0.4)))));

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
    vec3 color_grass = texture(tex_grass, TexCoord * 40.0).rgb;
    vec3 color_rock = texture(tex_rock, TexCoord * 40.0).rgb;
    vec3 color_lava = texture(tex_lava, TexCoord * 15.0 + vec2(time * 0.03, time * 0.03)).rgb; 

    vec3 norm = normalize(Normal);
    float slope = 1.0 - norm.y;

    float h = FragPos.y;
    vec3 base_color;

    float grass_rock_mix = smoothstep(15.0, 35.0, h);
    base_color = mix(color_grass, color_rock, grass_rock_mix);

    float slope_factor = smoothstep(0.4, 0.8, slope);
    base_color = mix(base_color, color_rock * 0.8, slope_factor);

    float dist_crater = length(FragPos.xz);
    float ash_dist = 1.0 - smoothstep(5.0, ash_radius, dist_crater);
    float ash_heat = smoothstep(40.0, 70.0, h);
    float ash_amount = ash_dist * (1.0 - ash_heat) * ash_intensity;
    vec3 ash_tint = vec3(0.12, 0.10, 0.08);
    base_color = mix(base_color, ash_tint, ash_amount);

    if (h > 80.0) {
        float lava_factor = smoothstep(80.0, 92.0, h);
        float dist_center = length(FragPos.xz);
        float pulse_intensity = smoothstep(12.0, 5.0, dist_center);

        float pulse = 0.92 + 0.08 * sin(time * 2.5) + 0.04 * sin(time * 6.3);
        pulse *= pulse_intensity + 0.5;
        vec3 glowing_lava = color_lava * pulse * 2.0;

        float bloom = pow(lava_factor, 2.5) * 1.2;
        base_color = mix(base_color, glowing_lava + vec3(1.0, 0.4, 0.1) * bloom * 1.5, lava_factor);
    }

    vec3 view_dir = normalize(cam_pos - FragPos);

    vec3 sun_dir = normalize(vec3(0.6, 1.0, 0.4));
    vec3 sun_color = vec3(1.0, 0.95, 0.85);

    float diff_sun = max(dot(norm, sun_dir), 0.0);
    vec3 halfway_sun = normalize(sun_dir + view_dir);
    float spec_sun = pow(max(dot(norm, halfway_sun), 0.0), 32.0);

    float ao = mix(0.4, 1.0, smoothstep(-20.0, 30.0, h));
    ao *= mix(0.6, 1.0, smoothstep(0.3, 0.8, 1.0 - slope));

    float shad = shadow_factor(FragPos);
    vec3 lighting = (0.25 * ao + 0.75 * diff_sun * shad) * sun_color * base_color;
    lighting += spec_sun * 0.2 * sun_color * shad;

    vec3 l_dir = normalize(light_pos - FragPos);
    float dist = length(light_pos - FragPos);
    float attenuation = 1.0 / (1.0 + 0.005 * dist + 0.0002 * dist * dist);

    float diff_lava = max(dot(norm, l_dir), 0.0);

    float flicker = 0.85 + 0.15 * sin(time * 3.0) + 0.05 * sin(time * 5.0);
    vec3 lava_light = vec3(1.0, 0.35, 0.05) * flicker * 3.0;

    vec3 halfway_lava = normalize(l_dir + view_dir);
    float spec_lava = pow(max(dot(norm, halfway_lava), 0.0), 24.0);

    lighting += (diff_lava * 0.8 + spec_lava * 0.4) * lava_light * base_color * attenuation;

    float rim = 1.0 - max(dot(view_dir, norm), 0.0);
    rim = pow(rim, 3.0);
    if (h > 70.0) {
        float rim_factor = smoothstep(70.0, 95.0, h);
        vec3 rim_color = vec3(1.0, 0.4, 0.0) * (0.7 + 0.3 * sin(time * 2.0));
        lighting += rim * rim_factor * rim_color * 0.6;
    }

    float dist_cam = length(cam_pos - FragPos);
    float fog_factor = exp(-pow((dist_cam * fog_density), 2.0));
    fog_factor = clamp(fog_factor, 0.0, 1.0);

    vec3 final_color = mix(fog_color, lighting, fog_factor);

    FragColor = vec4(final_color, 1.0);
}
