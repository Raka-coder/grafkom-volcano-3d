#version 330 core

in vec2 TexCoord;
out vec4 FragColor;

uniform float time;
uniform vec3 fog_color;

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
    for (int i = 0; i < 5; ++i) {
        v += a * noise(p);
        p = rot * p * 2.0 + shift;
        a *= 0.5;
    }
    return v;
}

void main() {
    // 1. Sky Dome Gradient (Atmospheric Scattering palsu)
    // Gunakan TexCoord.y (ketinggian) untuk gradasi dari horizon ke zenit
    float altitude = clamp(TexCoord.y / 10.0, 0.0, 1.0);
    vec3 sky_zenith = vec3(0.2, 0.4, 0.8); // Biru tua di atas
    vec3 sky_horizon = fog_color;          // Warna fog di cakrawala
    vec3 sky_gradient = mix(sky_horizon, sky_zenith, altitude);

    // 2. Output akhir tanpa awan (Hanya gradasi langit)
    FragColor = vec4(sky_gradient, 1.0);
}
