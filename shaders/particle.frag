#version 330 core

in vec4 out_color;
out vec4 FragColor;

void main() {
    // gl_PointCoord memberikan UV default untuk point sprite (0.0 s.d 1.0)
    // Ubah rentang ke -1.0 s.d 1.0 untuk menghitung jarak ke tengah lingkaran
    vec2 circ_coord = 2.0 * gl_PointCoord - 1.0;
    
    // Menghitung gradasi alpha (bundar dan memudar di tepi)
    float alpha = 1.0 - length(circ_coord);
    
    // Buang pixel yang di luar lingkaran
    if (alpha <= 0.0) discard;
    
    // Hasil warna partikel menggunakan alpha blend dari shader + soft edge dari sprite
    FragColor = vec4(out_color.rgb, out_color.a * alpha);
}
