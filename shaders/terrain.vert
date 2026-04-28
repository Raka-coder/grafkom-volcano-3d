#version 330 core

// Atribut Vertex
in vec3 in_position;
in vec3 in_normal;
in vec2 in_texcoord;

// Output ke Fragment Shader
out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoord;

// Uniform Matrices (Transformasi Kamera & Objek)
uniform mat4 m_model;
uniform mat4 m_view;
uniform mat4 m_proj;

void main() {
    // 1. Transformasi posisi vertex ke World Space
    FragPos = vec3(m_model * vec4(in_position, 1.0));
    
    // 2. Transformasi Normal Vector agar tetap tegak lurus jika model di-scale/rotate
    Normal = mat3(transpose(inverse(m_model))) * in_normal;  
    
    // 3. Meneruskan UV Texture Coordinate
    TexCoord = in_texcoord;
    
    // 4. Posisi akhir vertex di Screen Space
    gl_Position = m_proj * m_view * vec4(FragPos, 1.0);
}
