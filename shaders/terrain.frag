#version 330 core

// Input dari Vertex Shader
in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;

// Output akhir berupa warna pixel di layar
out vec4 FragColor;

// Uniforms Kamera & Lighting
uniform vec3 cam_pos;
uniform vec3 light_pos;
uniform float time;

// Tekstur yang diload
uniform sampler2D tex_grass;
uniform sampler2D tex_rock;
uniform sampler2D tex_lava;

// Konfigurasi Kabut (Fog)
uniform vec3 fog_color = vec3(0.5, 0.6, 0.7);
uniform float fog_density = 0.003;

void main() {
    // --- 1. Texture Mapping & Smart Blending ---
    // Tiling texture agar detail tetap tajam di area luas
    vec3 color_grass = texture(tex_grass, TexCoord * 40.0).rgb;
    vec3 color_rock = texture(tex_rock, TexCoord * 40.0).rgb;
    vec3 color_lava = texture(tex_lava, TexCoord * 15.0 + vec2(time * 0.03, time * 0.03)).rgb; 
    
    vec3 norm = normalize(Normal);
    float slope = 1.0 - norm.y; // 0.0 = rata, 1.0 = vertikal
    
    float h = FragPos.y;
    vec3 base_color;

    // Gradasi ketinggian yang lebih halus dengan 3 transition zones
    float grass_rock_mix = smoothstep(15.0, 35.0, h);
    base_color = mix(color_grass, color_rock, grass_rock_mix);
    
    // Tambahan tekstur batu pada area curam (slope-based blending)
    float slope_factor = smoothstep(0.4, 0.8, slope);
    base_color = mix(base_color, color_rock * 0.8, slope_factor);
    
    // Efek kawah lava di puncak gunung (dengan Bloom/Glow yang lebih dramatis)
    if (h > 75.0) {
        float lava_factor = smoothstep(75.0, 95.0, h);
        
        // Hanya kedip intens di dalam kawah
        float dist_center = length(FragPos.xz);
        float pulse_intensity = smoothstep(15.0, 8.0, dist_center); 
        
        // Flicker yang lebih natural dengan 2 frequencies
        float pulse = 0.85 + 0.15 * sin(time * 2.5) + 0.08 * sin(time * 6.3);
        pulse *= pulse_intensity + 0.5;
        vec3 glowing_lava = color_lava * pulse * 2.0;
        
        // Efek Bloom: Lava yang sangat terang memberikan pendaran cahaya (glow)
        float bloom = pow(lava_factor, 2.5) * 1.2;
        base_color = mix(base_color, glowing_lava + vec3(1.0, 0.4, 0.1) * bloom * 1.5, lava_factor);
    }
    
    // --- 2. Advanced Blinn-Phong Lighting Model ---
    vec3 view_dir = normalize(cam_pos - FragPos);
    
    // A. Direct Sun Light (Main Source)
    vec3 sun_dir = normalize(vec3(0.6, 1.0, 0.4));
    vec3 sun_color = vec3(1.0, 0.95, 0.85);
    
    float diff_sun = max(dot(norm, sun_dir), 0.0);
    vec3 halfway_sun = normalize(sun_dir + view_dir);
    float spec_sun = pow(max(dot(norm, halfway_sun), 0.0), 32.0);  // Higher shininess
    
    // Ambient occlusion berdasarkan ketinggian dan slope
    float ao = mix(0.4, 1.0, smoothstep(-20.0, 30.0, h));
    ao *= mix(0.6, 1.0, smoothstep(0.3, 0.8, 1.0 - slope));
    
    vec3 lighting = (0.25 * ao + 0.75 * diff_sun) * sun_color * base_color;
    lighting += spec_sun * 0.2 * sun_color;
    
    // B. Magma Glow (Point Light dari kawah)
    vec3 l_dir = normalize(light_pos - FragPos);
    float dist = length(light_pos - FragPos);
    float attenuation = 1.0 / (1.0 + 0.005 * dist + 0.0002 * dist * dist);
    
    float diff_lava = max(dot(norm, l_dir), 0.0);
    
    // Flicker pattern untuk cahaya lava yang natural
    float flicker = 0.7 + 0.3 * sin(time * 4.0) + 0.15 * sin(time * 2.7);
    vec3 lava_light = vec3(1.0, 0.35, 0.05) * flicker * 3.0;
    
    // Specular reflection dari cahaya lava
    vec3 halfway_lava = normalize(l_dir + view_dir);
    float spec_lava = pow(max(dot(norm, halfway_lava), 0.0), 24.0);
    
    lighting += (diff_lava * 0.8 + spec_lava * 0.4) * lava_light * base_color * attenuation;
    
    // --- 3. Rim Lighting (Halo effect di tepi lava) ---
    float rim = 1.0 - max(dot(view_dir, norm), 0.0);
    rim = pow(rim, 3.0);
    if (h > 70.0) {
        float rim_factor = smoothstep(70.0, 95.0, h);
        vec3 rim_color = vec3(1.0, 0.4, 0.0) * (0.5 + 0.5 * sin(time * 3.0));
        lighting += rim * rim_factor * rim_color * 0.6;
    }
    
    // --- 4. Atmosphere & Fog ---
    float dist_cam = length(cam_pos - FragPos);
    float fog_factor = exp(-pow((dist_cam * fog_density), 2.0));
    fog_factor = clamp(fog_factor, 0.0, 1.0);
    
    vec3 final_color = mix(fog_color, lighting, fog_factor);
    
    FragColor = vec4(final_color, 1.0);
}
