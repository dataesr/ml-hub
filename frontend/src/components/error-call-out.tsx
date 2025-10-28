import { CallOut } from "@codegouvfr/react-dsfr/CallOut"

export default function ErrorCallOut({ error }: { error: unknown }) {
  console.log("error", error)

  return (
    <CallOut title="Error while loading data">
      {error instanceof Error ? `Error: ${error.message}` : `Error: please check logs`}
    </CallOut>
  )
}
