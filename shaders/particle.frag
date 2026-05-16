#version 330 core

in vec4 out_color;
out vec4 FragColor;

uniform float time = 0.0;

void main() {
    vec2 uv = 2.0 * gl_PointCoord - 1.0;
    float dist = length(uv);

    float angle = atan(uv.y, uv.x);
    float r = 0.90 + sin(angle * 5.0 + dist * 3.0 + time * 1.2) * 0.10;

    float alpha = 1.0 - smoothstep(r * 0.5, r + 0.20, dist);

    FragColor = vec4(out_color.rgb, out_color.a * alpha);
}
