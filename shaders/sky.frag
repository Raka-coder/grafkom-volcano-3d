#version 330 core

in vec2 TexCoord;
in vec3 FragPos;
out vec4 FragColor;

uniform float time;
uniform vec3 fog_color;
uniform vec3 cam_pos;

// Fungsi noise sederhana untuk awan (Fractal Brownian Motion)
float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

float fbm(vec2 p) {
    float v = 0.0;
    float a = 0.5;
    vec2 shift = vec2(100.0);
    mat2 rot = mat2(cos(0.5), sin(0.5), -sin(0.5), cos(0.5));
    for (int i = 0; i < 6; ++i) {
        v += a * noise(p + time * 0.1);
        p = rot * p * 2.0 + shift;
        a *= 0.5;
    }
    return v;
}

void main() {
    // 1. Sky Dome Gradient (Realistic Atmospheric Scattering)
    // Gradient dari horizon ke zenith dengan warna yang lebih dramatis
    float altitude = clamp(TexCoord.y / 10.0, 0.0, 1.0);
    
    // Multi-layer gradient untuk kedalaman atmosfer
    vec3 sky_zenith = vec3(0.15, 0.35, 0.85);      // Biru tua di atas
    vec3 sky_mid = vec3(0.4, 0.6, 0.95);           // Biru terang di tengah
    vec3 sky_horizon = vec3(1.0, 0.8, 0.6);        // Oranye-kuning di cakrawala
    
    vec3 sky_color = sky_zenith;
    if (altitude < 0.5) {
        sky_color = mix(sky_horizon, sky_mid, altitude * 2.0);
    } else {
        sky_color = mix(sky_mid, sky_zenith, (altitude - 0.5) * 2.0);
    }
    
    // 2. Cloud Rendering dengan FBM
    vec2 cloud_uv = TexCoord + vec2(time * 0.02, 0.0);
    float cloud_noise = fbm(cloud_uv * 3.0);
    float cloud_pattern = smoothstep(0.3, 0.7, cloud_noise);
    
    // Cloud color dengan gradasi
    vec3 cloud_light = vec3(1.0, 0.95, 0.9);
    vec3 cloud_shadow = vec3(0.5, 0.6, 0.8);
    vec3 cloud_color = mix(cloud_shadow, cloud_light, cloud_pattern);
    
    // Blend clouds dengan langit
    sky_color = mix(sky_color, cloud_color, cloud_pattern * 0.4);
    
    // 3. Sun Disk - Bola matahari di cakrawala
    vec2 sun_pos = vec2(0.3, 0.15);  // Posisi matahari (normalized coordinates)
    float sun_dist = distance(TexCoord / 10.0, sun_pos);
    
    float sun_core = smoothstep(0.12, 0.08, sun_dist);
    float sun_glow = smoothstep(0.25, 0.1, sun_dist) * 0.6;
    
    vec3 sun_color = vec3(1.0, 0.9, 0.5) * (sun_core + sun_glow);
    sky_color += sun_color;
    
    // 4. Add drama: darker regions di cloud shadows
    float shadow_intensity = fbm(cloud_uv * 5.0 + time * 0.05);
    sky_color *= mix(0.7, 1.0, smoothstep(-0.3, 0.5, shadow_intensity));
    
    // 5. Tone mapping untuk mencegah overexposure
    sky_color = sky_color / (sky_color + vec3(1.0));
    
    FragColor = vec4(sky_color, 1.0);
}
