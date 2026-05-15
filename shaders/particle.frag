#version 330 core

in vec4 out_color;
out vec4 FragColor;

void main() {
    vec2 circ_coord = 2.0 * gl_PointCoord - 1.0;
    float dist = length(circ_coord);
    
    if (dist > 1.0) discard;
    
    float alpha = 1.0 - smoothstep(0.0, 1.0, dist);
    alpha *= alpha;
    
    FragColor = vec4(out_color.rgb, out_color.a * alpha);
}
