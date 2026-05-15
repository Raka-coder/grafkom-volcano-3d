#version 330 core

in vec2 TexCoord;
out vec4 FragColor;

uniform float time;
uniform vec3 glow_color = vec3(1.0, 0.4, 0.05);
uniform float intensity = 1.0;

void main() {
    vec2 center = TexCoord - vec2(0.5);
    float dist = length(center) * 2.0;

    float edge = 1.0 - smoothstep(0.0, 1.0, dist);
    float glow = edge * edge;

    float pulse = 0.85 + 0.15 * sin(time * 2.0);

    FragColor = vec4(glow_color * glow * pulse * intensity, glow * 0.4);
}
