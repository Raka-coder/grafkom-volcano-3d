#version 330 core

in vec3 in_position;

uniform mat4 m_model;
uniform mat4 light_space;

void main() {
    gl_Position = light_space * m_model * vec4(in_position, 1.0);
}
