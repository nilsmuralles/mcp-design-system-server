// Fixture de demo para mcp-design-system-server.
// Contiene violaciones intencionales del Design System (data/design_tokens.json):
//   1. Color de fondo hardcodeado (#ff6600) que no existe en la paleta de tokens.
//   2. font-size (14px) fuera de la escala tipográfica (12/16/24/32px).
//   3. padding (10px) fuera de la escala de espaciado (4/8/16/24/32px).
//   4. Texto blanco (#ffffff) sobre el fondo naranja (#ff6600): contraste insuficiente
//      para texto normal según WCAG AA (ratio < 4.5).

function Button({ label }) {
  return (
    <button
      style={{
        backgroundColor: "#ff6600",
        color: "#ffffff",
        fontSize: "14px",
        padding: "10px",
      }}
    >
      {label}
    </button>
  );
}

export default Button;
