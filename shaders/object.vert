#version 330 core

in vec3 in_position;
in vec3 in_normal;
in vec3 in_color;

out vec3 FragPos;
out vec3 Normal;
out vec3 Color;

uniform mat4 m_model;
uniform mat4 m_view;
uniform mat4 m_proj;

void main() {
    FragPos = vec3(m_model * vec4(in_position, 1.0));
    Normal = mat3(transpose(inverse(m_model))) * in_normal;
    Color = in_color;
    gl_Position = m_proj * m_view * vec4(FragPos, 1.0);
}
