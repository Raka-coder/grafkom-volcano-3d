#version 330 core

layout(location = 0) in vec3 in_position;
layout(location = 1) in vec2 in_texcoord;

out vec2 TexCoord;

uniform mat4 view;
uniform mat4 projection;
uniform vec3 cam_pos;

void main() {
    // Geser sky plane mengikuti kamera secara horizontal
    vec3 pos = in_position;
    pos.x += cam_pos.x;
    pos.z += cam_pos.z;
    
    gl_Position = projection * view * vec4(pos, 1.0);
    TexCoord = in_texcoord + vec2(cam_pos.x * 0.001, cam_pos.z * 0.001);
}
