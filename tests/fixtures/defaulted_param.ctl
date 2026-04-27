void main(varying float rIn, varying float gIn, varying float bIn,
          output varying float rOut, output varying float gOut, output varying float bOut,
          float scale = 2.0)
{
    rOut = rIn * scale; gOut = gIn * scale; bOut = bIn * scale;
}
