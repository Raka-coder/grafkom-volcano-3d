#version 330 core

in vec2 TexCoord;
out vec4 FragColor;

uniform float time;

void main() {
    float dist_from_center = abs(TexCoord.x - 0.5) * 2.0;
    float edge = 1.0 - dist_from_center;
    edge = pow(edge, 1.8);

    float flow = TexCoord.y * 2.0 + time * 0.4;
    float flow_pattern = sin(flow * 2.0) * 0.3 + sin(flow * 3.7 + 1.2) * 0.15;
    flow_pattern = flow_pattern * 0.5 + 0.5;

    float vein = sin(TexCoord.x * 12.0 + flow * 1.5) * 0.5 + 0.5;
    vein = pow(vein, 4.0);

    float pulse = 0.85 + 0.15 * sin(time * 2.0 + TexCoord.y * 4.0);
    float glow_pulse = 0.7 + 0.3 * sin(time * 1.3 + TexCoord.y * 2.0);

    vec3 hot_core = vec3(1.0, 0.7, 0.05);
    vec3 mid = vec3(0.9, 0.35, 0.02);
    vec3 edge_color = vec3(0.5, 0.08, 0.01);

    vec3 lava = mix(edge_color, mid, edge * pulse);
    lava = mix(lava, hot_core, edge * edge * flow_pattern * pulse);
    lava += vec3(1.0, 0.6, 0.0) * vein * 0.3 * edge;
    lava += vec3(1.0, 0.3, 0.0) * glow_pulse * 0.2 * edge;

    float alpha = edge * 0.95;
    FragColor = vec4(lava, alpha);
}
