#version 330 core

in vec2 TexCoord;
in vec3 FragPos;
out vec4 FragColor;

uniform float time;
uniform vec3 fog_color;
uniform vec3 cam_pos;

void main() {
    float altitude = clamp(TexCoord.y / 10.0, 0.0, 1.0);

    vec3 sky_zenith = vec3(0.3, 0.55, 0.95);
    vec3 sky_upper = vec3(0.5, 0.7, 1.0);
    vec3 sky_mid = vec3(0.7, 0.85, 1.0);
    vec3 sky_horizon = vec3(0.85, 0.88, 0.95);

    vec3 sky_color;
    if (altitude < 0.33) {
        sky_color = mix(sky_horizon, sky_mid, altitude * 3.0);
    } else if (altitude < 0.66) {
        sky_color = mix(sky_mid, sky_upper, (altitude - 0.33) * 3.0);
    } else {
        sky_color = mix(sky_upper, sky_zenith, (altitude - 0.66) * 3.0);
    }

    vec2 screen_uv = TexCoord / 10.0;
    vec2 sun_pos = vec2(0.3, 0.15);
    float sun_dist = distance(screen_uv, sun_pos);

    float sun_core = smoothstep(0.1, 0.03, sun_dist);
    float sun_glow = smoothstep(0.5, 0.06, sun_dist) * 0.5;
    sky_color += vec3(1.0, 0.95, 0.6) * (sun_core + sun_glow);

    sky_color = clamp(sky_color, 0.0, 1.0);

    FragColor = vec4(sky_color, 1.0);
}
