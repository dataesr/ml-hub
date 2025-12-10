import { Container } from "@dataesr/dsfr-plus"

interface CopyToClipboardArgs {
  children: JSX.Element
  copyText: string
}

export default function CopyToClipboard({ children, copyText }: CopyToClipboardArgs) {
  return (
    <Container
      fluid
      onClick={() => {
        navigator.clipboard.writeText(copyText)
      }}
      style={{ cursor: "pointer" }}
    >
      {children}
    </Container>
  )
}
