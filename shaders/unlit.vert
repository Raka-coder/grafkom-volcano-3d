#version 330 core

in vec3 in_position;
in vec3 in_color;

out vec3 Color;

uniform mat4 m_proj;
uniform mat4 m_view;

void main() {
    gl_Position = m_proj * m_view * vec4(in_position, 1.0);
    Color = in_color;
}
