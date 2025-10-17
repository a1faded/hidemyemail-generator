import asyncio
import datetime
import os
from typing import Union, List, Optional
import re
import time

from rich.text import Text
from rich.prompt import IntPrompt
from rich.console import Console
from rich.table import Table

from icloud import HideMyEmail


MAX_CONCURRENT_TASKS = 10
RATE_LIMIT_BATCH_SIZE = 5  # Apple's limit: 5 emails per batch
RATE_LIMIT_WAIT_TIME = 2700  # 45 minutes in seconds


class RichHideMyEmail(HideMyEmail):
    _cookie_file = "cookie.txt"

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.table = Table()

        if os.path.exists(self._cookie_file):
            # load in a cookie string from file
            with open(self._cookie_file, "r") as f:
                self.cookies = [line for line in f if not line.startswith("//")][0]
        else:
            self.console.log(
                '[bold yellow][WARN][/] No "cookie.txt" file found! Generation might not work due to unauthorized access.'
            )

    async def _generate_one(self) -> Union[str, None]:
        # First, generate an email
        gen_res = await self.generate_email()

        if not gen_res:
            return
        elif "success" not in gen_res or not gen_res["success"]:
            error = gen_res["error"] if "error" in gen_res else {}
            err_msg = "Unknown"
            if type(error) == int and "reason" in gen_res:
                err_msg = gen_res["reason"]
            elif type(error) == dict and "errorMessage" in error:
                err_msg = error["errorMessage"]
            self.console.log(
                f"[bold red][ERR][/] - Failed to generate email. Reason: {err_msg}"
            )
            return

        email = gen_res["result"]["hme"]
        self.console.log(f'[50%] "{email}" - Successfully generated')

        # Then, reserve it
        reserve_res = await self.reserve_email(email)

        if not reserve_res:
            return
        elif "success" not in reserve_res or not reserve_res["success"]:
            error = reserve_res["error"] if "error" in reserve_res else {}
            err_msg = "Unknown"
            if type(error) == int and "reason" in reserve_res:
                err_msg = reserve_res["reason"]
            elif type(error) == dict and "errorMessage" in error:
                err_msg = error["errorMessage"]
            self.console.log(
                f'[bold red][ERR][/] "{email}" - Failed to reserve email. Reason: {err_msg}'
            )
            return

        self.console.log(f'[100%] "{email}" - Successfully reserved')
        return email

    async def _generate(self, num: int):
        tasks = []
        for _ in range(num):
            task = asyncio.ensure_future(self._generate_one())
            tasks.append(task)

        return filter(lambda e: e is not None, await asyncio.gather(*tasks))

    async def _wait_with_countdown(self, seconds: int):
        """Wait for specified seconds with a countdown display"""
        from rich.live import Live
        from rich.text import Text
        
        end_time = time.time() + seconds
        
        with Live(console=self.console, refresh_per_second=1) as live:
            while time.time() < end_time:
                remaining = int(end_time - time.time())
                mins, secs = divmod(remaining, 60)
                
                text = Text()
                text.append("⏳ Rate limit reached. Waiting ", style="bold yellow")
                text.append(f"{mins:02d}:{secs:02d}", style="bold cyan")
                text.append(" before next batch...", style="bold yellow")
                
                live.update(text)
                await asyncio.sleep(1)

    async def generate(self, count: Optional[int]) -> List[str]:
        try:
            emails = []
            self.console.rule()
            if count is None:
                s = IntPrompt.ask(
                    Text.assemble(("How many iCloud emails you want to generate?")),
                    console=self.console,
                )

                count = int(s)
            self.console.log(f"Generating {count} email(s)...")
            self.console.rule()

            total_to_generate = count
            batches_needed = (count + RATE_LIMIT_BATCH_SIZE - 1) // RATE_LIMIT_BATCH_SIZE
            current_batch = 0

            while count > 0:
                batch_size = min(count, RATE_LIMIT_BATCH_SIZE)
                
                self.console.log(f"[bold cyan]Batch {current_batch + 1}/{batches_needed}[/] - Generating {batch_size} email(s)...")
                
                with self.console.status(f"[bold green]Generating iCloud email(s)..."):
                    batch = [*await self._generate(
                        batch_size if batch_size < MAX_CONCURRENT_TASKS else MAX_CONCURRENT_TASKS
                    )]
                
                # Check if batch was successful
                if len(batch) == 0:
                    # All failed - likely rate limited
                    self.console.log(f"[bold red]✗[/] All emails in this batch were rate limited.")
                    await self._wait_with_countdown(RATE_LIMIT_WAIT_TIME)
                    self.console.log("[bold green]✓[/] Wait complete. Retrying batch...")
                    self.console.rule()
                    continue  # Retry this batch without counting it
                
                # Batch was at least partially successful
                emails += batch
                
                # Save to file immediately after each batch
                if len(batch) > 0:
                    with open("emails.txt", "a+") as f:
                        f.write(os.linesep.join(batch) + os.linesep)
                
                count -= len(batch)
                current_batch += 1

                # If there are more emails to generate, wait for the rate limit
                if count > 0:
                    self.console.log(f"[bold green]✓[/] Batch {current_batch} complete. {len(emails)}/{total_to_generate} emails generated so far.")
                    await self._wait_with_countdown(RATE_LIMIT_WAIT_TIME)
                    self.console.log("[bold green]✓[/] Wait complete. Continuing with next batch...")
                    self.console.rule()

            if len(emails) > 0:
                self.console.rule()
                self.console.log(
                    f':star: All emails have been saved to the "emails.txt" file'
                )

                self.console.log(
                    f"[bold green]All done![/] Successfully generated [bold green]{len(emails)}[/] email(s)"
                )

            return emails
        except KeyboardInterrupt:
            return []

    async def list(self, active: bool, search: str) -> None:
        gen_res = await self.list_email()
        if not gen_res:
            return

        if "success" not in gen_res or not gen_res["success"]:
            error = gen_res["error"] if "error" in gen_res else {}
            err_msg = "Unknown"
            if type(error) == int and "reason" in gen_res:
                err_msg = gen_res["reason"]
            elif type(error) == dict and "errorMessage" in error:
                err_msg = error["errorMessage"]
            self.console.log(
                f"[bold red][ERR][/] - Failed to generate email. Reason: {err_msg}"
            )
            return

        self.table.add_column("Label")
        self.table.add_column("Hide my email")
        self.table.add_column("Created Date Time")
        self.table.add_column("IsActive")

        for row in gen_res["result"]["hmeEmails"]:
            if row["isActive"] == active:
                if search is not None and re.search(search, row["label"]):
                    self.table.add_row(
                        row["label"],
                        row["hme"],
                        str(
                            datetime.datetime.fromtimestamp(
                                row["createTimestamp"] / 1000
                            )
                        ),
                        str(row["isActive"]),
                    )
                else:
                    self.table.add_row(
                        row["label"],
                        row["hme"],
                        str(
                            datetime.datetime.fromtimestamp(
                                row["createTimestamp"] / 1000
                            )
                        ),
                        str(row["isActive"]),
                    )

        self.console.print(self.table)


async def generate(count: Optional[int]) -> None:
    async with RichHideMyEmail() as hme:
        await hme.generate(count)


async def list(active: bool, search: str) -> None:
    async with RichHideMyEmail() as hme:
        await hme.list(active, search)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(generate(None))
    except KeyboardInterrupt:
        pass
