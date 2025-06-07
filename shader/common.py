
# Utilities for functions used by both vertex and fragment shaders.
include_ = '''
        vec4 mulVec(mat4 matrix, vec3 a) {
            return matrix * vec4(a, 1);
        }
'''

# A library of distance functions and mathematical utilities.
include_frag_ = '''
        mat4 rotmat(vec3 axis, in float angle) {
            axis = normalize(axis);
            float s = sin(angle);
            float c = cos(angle);
            float oc = 1.0 - c;
            
            return mat4(oc * axis.x * axis.x + c,           oc * axis.x * axis.y - axis.z * s,  oc * axis.z * axis.x + axis.y * s,  0.0,
                        oc * axis.x * axis.y + axis.z * s,  oc * axis.y * axis.y + c,           oc * axis.y * axis.z - axis.x * s,  0.0,
                        oc * axis.z * axis.x - axis.y * s,  oc * axis.y * axis.z + axis.x * s,  oc * axis.z * axis.z + c,           0.0,
                        0.0,                                0.0,                                0.0,                                1.0);
        }
        
        // https://qiita.com/ukonpower/items/ebafd19fcb33f37ed273
        mat4 qua2mat( in vec4 q ){
            mat4 m = mat4(
                +1.0 - 2.0 * pow( q.x, 2.0 ) - 2.0 * pow( q.y, 2.0 ), +2.0 * q.z * q.x + 2.0 * q.w * q.y, +2.0 * q.z * q.y - 2.0 * q.w * q.x, 0.0,
                -2.0 * q.z * q.y - 2.0 * q.w * q.x, -2.0 * q.x * q.y + 2.0 * q.w * q.z, -1.0 + 2.0 * pow( q.z, 2.0 ) + 2.0 * pow( q.x, 2.0 ), 0.0,
                +2.0 * q.z * q.x - 2.0 * q.w * q.y, +1.0 - 2.0 * pow( q.z, 2.0 ) - 2.0 * pow( q.y, 2.0 ), +2.0 * q.x * q.y + 2.0 * q.w * q.z, 0.0,
                0.0, 0.0, 0.0, 1.0
            );
            return m;
        }

        float dot2( in vec2 v ) { return dot(v,v); }
        float dot2( in vec3 v ) { return dot(v,v); }
        float ndot( in vec2 a, in vec2 b ) { return a.x*b.x - a.y*b.y; }

        float opRound( in float d, in float h )
        {
            return d - h;
        }
        
        float opExtrusion( in vec3 p, in float dist, in float h )
        {
            vec2 w = vec2( dist, abs(p.z) - h );
            return min(max(w.x,w.y),0.0) + length(max(w,0.0));
        }
        
        float which(float v0, float v1, bool t) {
            return v0 * int(t) + v1 * (1.0 - int(t));
        }
        
        vec2 which(vec2 v0, vec2 v1, bool t) {
            return v0 * int(t) + v1 * (1.0 - int(t));
        }

        //
        // No Blending
        //

        float opUnion( in float d0, in float d1 )
        {
            return min(d0,d1);
        }
        float opDifference( in float d0, in float d1 )
        {
            return max(-d0,d1);
        }
        float opIntersection( in float d0, in float d1 )
        {
            return max(d0,d1);
        }

        //
        // Smooth
        //
        
        float opSmoothUnion( in float d0, in float d1, in float k )
        {
            float h = clamp( 0.5 + 0.5*(d1-d0)/k, 0.0, 1.0 );
            return mix( d1, d0, h ) - k*h*(1.0-h);
        }
        float opSmoothDifference( in float d0, in float d1, in float k )
        {
            float h = clamp( 0.5 - 0.5*(d1+d0)/k, 0.0, 1.0 );
            return mix( d1, -d0, h ) + k*h*(1.0-h);
        }
        float opSmoothIntersection( in float d0, in float d1, in float k )
        {
            float h = clamp( 0.5 - 0.5*(d1-d0)/k, 0.0, 1.0 );
            return mix( d1, d0, h ) + k*h*(1.0-h);
        }

        // -----------------------------------------------------------------------------------------------
        // https://mercury.sexy/hg_sdf/
        //

        //
        // Round
        //
        
        float opRoundUnion( in float d0, in float d1, in float r )
        {
            vec2 u = max(vec2(r - d0, r - d1), vec2(0));
            return max(r, min (d0, d1)) - length(u);
        }
        float opRoundDifference( in float d0, in float d1, in float r )
        {
            return opRoundUnion(d0, -d1, r);
        }
        float opRoundIntersection( in float d0, in float d1, in float r )
        {
            vec2 u = max(vec2(r + d0, r + d1), vec2(0));
            return min(-r, max (d0, d1)) + length(u);
        }

        // s: champferSize
        float opChampferUnion( in float d0, in float d1, in float s) {
            const float SQRT05 = 0.70710678118;
            return min(min(d0, d1), (d0 - s + d1)*SQRT05);
        }
        float opChampferDifference( in float d0, in float d1, in float s) {
            return opChampferUnion(d0, -d1, s);
        }
        float opChampferIntersection( in float d0, in float d1, in float s) {
            const float SQRT05 = 0.70710678118;
            return max(max(d0, d1), (d0 + s + d1)*SQRT05);
        }
        
        float opStairsUnion( in float d0, in float d1, in float s, in float n) {
            float _s = s/n;
            float u = d1-_s;
            return min(min(d0,d1), 0.5 * (u + d0 + abs ((mod (u - d0 + _s, 2 * _s)) - _s)));
        }
        float opStairsDifference( in float d0, in float d1, in float s, in float n) {
            return -opStairsUnion(-d0, d1, s, n);
        }
        float opStairsIntersection( in float d0, in float d1, in float s, in float n) {
            return -opStairsUnion(-d0, -d1, s, n);
        }

        //
        // -----------------------------------------------------------------------------------------------

        float sdBox( in vec3 p, vec3 b, vec4 cr ) {
            b = b.xzy;
            cr.xy = which(cr.xy, cr.zw, (p.x>0.0));
            cr.x  = which(cr.x, cr.y, (p.y>0.0));
            vec2 q = abs(p.xy)-b.xy+cr.x;
            return opExtrusion(p, min(max(q.x,q.y),0.0) + length(max(q,0.0)) - cr.x, b.z);
        }
        float sdSphere( in vec3 p, in float r ) {
            return length(p)-r;
        }
        float sdCylinder( in vec3 p, in float h, in float r )
        {
            vec2 d = abs(vec2(length(p.xz),p.y)) - vec2(r,h);
            return min(max(d.x,d.y),0.0) + length(max(d,0.0));
        }
        float sdCappedCone( in vec3 p, in float h, in float r0, in float r1 )
        {
            vec2 q = vec2( length(p.xz), p.y );
            vec2 k1 = vec2(r1,h);
            vec2 k2 = vec2(r1-r0,2.0*h);
            vec2 ca = vec2(q.x-min(q.x,(q.y<0.0)?r0:r1), abs(q.y)-h);
            vec2 cb = q - k1 + k2*clamp( dot(k1-q,k2)/dot2(k2), 0.0, 1.0 );
            float s = which(-1.0, 1.0, (cb.x<0.0 && ca.y<0.0));
            return s*sqrt( min(dot2(ca),dot2(cb)) );
        }
        float sdCappedTorus( vec3 p, vec2 sc, float ra, float rb)
        {
            p.x = abs(p.x);
            float k = which(dot(p.xz,sc), length(p.xz), (sc.y*p.x>sc.x*p.z));
            return sqrt( dot(p,p) + ra*ra - 2.0*ra*k ) - rb;
        }
        float sdPyramid(vec3 p, float hw, float hd, float hh) {
            p.y += hh;
            p.xz = abs(p.xz);
            vec3 d1 = vec3(max(p.x - hw, 0.0), p.y, max(p.z - hd, 0.0));
            vec3 n1 = vec3(0.0, hd, 2.0 * hh);
            float k1 = dot(n1, n1);
            float h1 = dot(p - vec3(hw, 0.0, hd), n1) / k1;
            vec3 n2 = vec3(k1, 2.0 * hh * hw, -hd * hw);
            float m1 = dot(p - vec3(hw, 0.0, hd), n2) / dot(n2, n2);
            vec3 d2 = p - clamp(p - n1 * h1 - n2 * max(m1, 0.0), vec3(0.0), vec3(hw, 2.0 * hh, hd));
            vec3 n3 = vec3(2.0 * hh, hw, 0.0);
            float k2 = dot(n3, n3);
            float h2 = dot(p - vec3(hw, 0.0, hd), n3) / k2;
            vec3 n4 = vec3(-hw * hd, 2.0 * hh * hd, k2);
            float m2 = dot(p - vec3(hw, 0.0, hd), n4) / dot(n4, n4);    
            vec3 d3 = p - clamp(p - n3 * h2 - n4 * max(m2, 0.0), vec3(0.0), vec3(hw, 2.0 * hh, hd));
            float d = sqrt(min(min(dot(d1, d1), dot(d2, d2)), dot(d3, d3)));
            return which(-d, d, max(max(h1, h2), -p.y) < 0.0);
        }
        float sdTruncatedPyramid(vec3 p, float hw0, float hd0, float hw1, float hd1, float hh) {
            p.xz = abs(p.xz);
            vec3 d1 = vec3(max(p.x - hw0, 0.0), p.y + hh, max(p.z - hd0, 0.0));
            vec3 d2 = vec3(max(p.x - hw1, 0.0), p.y - hh, max(p.z - hd1, 0.0));
            vec3 e = vec3(hw0 - hw1, 2.0 * hh, hd0 - hd1);
            vec3 n1 = vec3(0.0, e.zy);
            float k1 = dot(n1, n1);
            float h1 = dot(p - vec3(hw0, -hh, hd0), n1) / k1;
            vec3 n2 = vec3(k1, e.y * e.x, -e.z * e.x);
            float m1 = dot(p - vec3(hw0, -hh, hd0), n2) / dot(n2, n2);
            vec3 d3 = p - clamp(p - n1 * h1 - n2 * max(m1, 0.0), vec3(0.0, -hh, 0.0), vec3(max(hw0, hw1), hh, max(hd0, hd1)));
            vec3 n3 = vec3(e.yx, 0.0);
            float k2 = dot(n3, n3);
            float h2 = dot(p - vec3(hw0, -hh, hd0), n3) / k2;
            vec3 n4 = vec3(-e.x * e.z, e.y * e.z, k2);
            float m2 = dot(p - vec3(hw0, -hh, hd0), n4) / dot(n4, n4);    
            vec3 d4 = p - clamp(p - n3 * h2 - n4 * max(m2, 0.0), vec3(0.0, -hh, 0.0), vec3(max(hw0, hw1), hh, max(hd0, hd1)));
            float d = sqrt(min(min(min(dot(d1, d1), dot(d2, d2)), dot(d3, d3)), dot(d4, d4)));
            return which(-d, d, max(max(h1, h2), abs(p.y) - hh) < 0.0);
        }
        float sdTriPrism( in vec3 p, in float h, in float r ) {
            vec3 q = abs(p);
            return max(q.y-h,max(q.x*0.866025+p.z*0.5,-p.z)-r*0.5);
        }
        float sdHexPrism( vec3 p, in float h, in float r ) {
            const vec3 k = vec3(-0.8660254, 0.5, 0.57735);
            p = abs(p);
            p.xz -= 2.0*min(dot(k.xy, p.xz), 0.0)*k.xy;
            vec2 d = vec2(
                length(p.xz-vec2(clamp(p.x,-k.z*r,k.z*r), r))*sign(p.z-r),
                p.y-h );
            return min(max(d.x,d.y),0.0) + length(max(d,0.0));
        }
        float sdNgonPrism( vec3 p, in float h, in float r, in float n) { // n: nsides
            const float PI = 3.14159;
        
            p = p.zxy;
        
            float theta, dist, side = n - 0.5, _h;
            vec2 a, b = vec2(r, 0), ba, pa;
            
            theta = (1.0 / n) * (2 * PI);
            a = b;
            b = vec2(r*cos(theta), r*sin(theta));
            
            ba = b-a;
            pa = p.xy-a;
            _h = clamp(dot(pa,ba)/dot(ba,ba),0.0,1.0);
            
            dist = length(pa-_h*ba);
            side -= sign((b.x-a.x)*(p.y-a.y)-(b.y-a.y)*(p.x-a.x));
            
            for (int i = 1; i < n; i++) {
                theta = ((i + 1) / n) * (2 * PI);
                a = b;
                b = vec2(r*cos(theta), r*sin(theta));
                
                ba = b-a;
                pa = p.xy-a;
                _h = clamp(dot(pa,ba)/dot(ba,ba),0.0,1.0);
                
                dist = min(length(pa-_h*ba),dist);
                side -= sign((b.x-a.x)*(p.y-a.y)-(b.y-a.y)*(p.x-a.x));
            }
            
            return opExtrusion(p, sign(side) * abs(dist), h);
        }
'''

# A library of fragment shader
# Investigation needed: For SDFObjectProp, when vec2 was used for the variable bl, 
# the data of the n+1 element of object_common_buffer was shifted 2 bytes behind 
# the intended position. This problem was solved by specifying vec4 for variable 
# bl, but needs to be investigated.
include_struct_ = '''
        struct SDFObjectProp {
            vec4 ps;  // position and scale
            vec4 qu;  // quaternion
            vec4 bl;  // blend
        };
        struct SDFBoxProp {
            vec4 br; // bound and round
            vec4 cr; // corner round
        };
        struct SDfSphereProp {
            float r; // radius
        };
        struct SDFCylinderProp {
            float h;  // height
            float ra; // radius
            float rd; // round
            float dm; // dummy
        };
        struct SDFTorusProp {
            float r0; // radius 0
            float r1; // radius 1
            vec2 sc;  // fill
        };
        struct SDFConeProp {
            float h;  // height
            float r0; // radius 0
            float r1; // radius 1
            float rd; // round
        };
        struct SDFPyramidProp {
            float hw; // half width
            float hd; // half depth
            float hh; // half hegiht
            float rd; // round
        };
        struct SDFTruncatedPyramidProp {
            float hw0; // half width 0
            float hd0; // half depth 0
            float hw1; // half width 1
            float hd1; // half depth 1
            float hh;  // half height
            float rd;  // round
        };
        struct SDFPrismProp {
            float h;  // height
            float ra; // radius
            float rd; // round
            float dm; // dummy
        };
        struct SDFNgonPrismProp {
            float h;  // height
            float ra; // radius
            float rd; // round
            float n;  // nsides
        };
'''