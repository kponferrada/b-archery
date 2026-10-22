"""DirectX text mesh writer, the same format as the game's own hand / ground
models. Taken from Jamie's Guilty Pleasures dev/make_models.py (known to load in
B42.21). Accepts a core.Mesh (v, n, t, tri) or anything with v, n, uv, f."""
import pathlib


class _Adapt:
    """Welds vertices that share position, normal and UV (core.Mesh keeps one per corner)."""

    def __init__(self, m):
        self.v, self.n, self.uv, self.f = [], [], [], []
        seen, idx = {}, []
        for p, n, t in zip(m.v, m.n, m.t):
            key = tuple(round(float(x), 5) for x in p) + tuple(round(float(x), 3) for x in n) + tuple(round(float(x), 5) for x in t)
            if key not in seen:
                seen[key] = len(self.v)
                self.v.append(tuple(float(x) for x in p))
                self.n.append(tuple(float(x) for x in n))
                self.uv.append(tuple(float(x) for x in t))
            idx.append(seen[key])
        for a, b, c in m.tri:
            tri = (idx[a], idx[b], idx[c])
            if len(set(tri)) == 3:
                self.f.append(tri)


def write(m, path, name, texture_file="JT.png"):
    write_x(_Adapt(m), pathlib.Path(path), name, texture_file)


def write_x(m, path, name, texture_file="JT.png"):
    out = ["xof 0303txt 0032"]
    out.append('''template ColorRGBA {
 <35ff44e0-6c7c-11cf-8f52-0040333594a3>
 FLOAT red;
 FLOAT green;
 FLOAT blue;
 FLOAT alpha;
}

template ColorRGB {
 <d3e16e81-7835-11cf-8f52-0040333594a3>
 FLOAT red;
 FLOAT green;
 FLOAT blue;
}

template Material {
 <3d82ab4d-62da-11cf-ab39-0020af71e433>
 ColorRGBA faceColor;
 FLOAT power;
 ColorRGB specularColor;
 ColorRGB emissiveColor;
 [...]
}

template TextureFilename {
 <a42790e1-7810-11cf-8f52-0040333594a3>
 STRING filename;
}

template Frame {
 <3d82ab46-62da-11cf-ab39-0020af71e433>
 [...]
}

template Matrix4x4 {
 <f6f23f45-7686-11cf-8f52-0040333594a3>
 array FLOAT matrix[16];
}

template FrameTransformMatrix {
 <f6f23f41-7686-11cf-8f52-0040333594a3>
 Matrix4x4 frameMatrix;
}

template Vector {
 <3d82ab5e-62da-11cf-ab39-0020af71e433>
 FLOAT x;
 FLOAT y;
 FLOAT z;
}

template MeshFace {
 <3d82ab5f-62da-11cf-ab39-0020af71e433>
 DWORD nFaceVertexIndices;
 array DWORD faceVertexIndices[nFaceVertexIndices];
}

template Mesh {
 <3d82ab44-62da-11cf-ab39-0020af71e433>
 DWORD nVertices;
 array Vector vertices[nVertices];
 DWORD nFaces;
 array MeshFace faces[nFaces];
 [...]
}

template MeshNormals {
 <f6f23f43-7686-11cf-8f52-0040333594a3>
 DWORD nNormals;
 array Vector normals[nNormals];
 DWORD nFaceNormals;
 array MeshFace faceNormals[nFaceNormals];
}

template MeshMaterialList {
 <f6f23f42-7686-11cf-8f52-0040333594a3>
 DWORD nMaterials;
 DWORD nFaceIndexes;
 array DWORD faceIndexes[nFaceIndexes];
 [Material <3d82ab4d-62da-11cf-ab39-0020af71e433>]
}

template Coords2d {
 <f6f23f44-7686-11cf-8f52-0040333594a3>
 FLOAT u;
 FLOAT v;
}

template MeshTextureCoords {
 <f6f23f40-7686-11cf-8f52-0040333594a3>
 DWORD nTextureCoords;
 array Coords2d textureCoords[nTextureCoords];
}

''')
    out.append(f'''Material {name}_Mat {{
 1.000000;1.000000;1.000000;1.000000;;
 10.000000;
 0.000000;0.000000;0.000000;;
 0.000000;0.000000;0.000000;;

 TextureFilename {{
  "{texture_file}";
 }}
}}
''')
    out.append(f"Frame {name} {{\n \n")
    out.append(" FrameTransformMatrix {\n  1.000000,0.000000,0.000000,0.000000,0.000000,1.000000,0.000000,0.000000,"
               "0.000000,0.000000,1.000000,0.000000,0.000000,0.000000,0.000000,1.000000;;\n }\n")
    faces = ",\n".join(f"  3;{a},{b},{c};" for a, b, c in m.f) + ";"
    out.append(f" Mesh {name} {{\n  {len(m.v)};")
    out.append(",\n".join(f"  {x:.6f};{y:.6f};{z:.6f};" for x, y, z in m.v) + ";")
    out.append(f"  {len(m.f)};\n{faces}\n")
    out.append(f"  MeshNormals {{\n   {len(m.n)};")
    out.append(",\n".join(f"   {x:.6f};{y:.6f};{z:.6f};" for x, y, z in m.n) + ";")
    out.append(f"   {len(m.f)};\n" + ",\n".join(f"   3;{a},{b},{c};" for a, b, c in m.f) + ";\n  }\n")
    out.append(f"  MeshMaterialList {{\n   1;\n   {len(m.f)};")
    out.append(",\n".join("   0" for _ in m.f) + ";")
    out.append(f"   {{ {name}_Mat }}\n  }}\n")
    out.append(f"  MeshTextureCoords c1 {{\n   {len(m.uv)};")
    out.append(",\n".join(f"   {u:.6f};{v:.6f};" for u, v in m.uv) + ";")
    out.append("  }\n }\n}")
    path.parent.mkdir(parents=True, exist_ok=True)
    # the game's own .x files use Windows line ends
    path.write_bytes("\n".join(out).replace("\n", "\r\n").encode("ascii"))


