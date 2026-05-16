#version 330 core

in vec3 in_position;
in vec4 in_color;
in float in_scale;

out vec4 out_color;

uniform mat4 m_view;
uniform mat4 m_proj;

void main() {
    out_color = in_color;
    gl_Position = m_proj * m_view * vec4(in_position, 1.0);
    
    // Menghitung ukuran partikel (point size) secara dinamis
    // Semakin jauh (dist besar), ukuran point semakin kecil
    float dist = length(gl_Position.xyz);
    gl_PointSize = (in_scale / dist) * 100.0;
    
    gl_PointSize = max(gl_PointSize, 6.0);
    gl_PointSize = min(gl_PointSize, 100.0);
}
