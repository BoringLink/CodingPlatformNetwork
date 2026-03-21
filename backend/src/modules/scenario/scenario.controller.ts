import { Controller, Get } from "@nestjs/common";
import { ScenarioService } from "./scenario.service";

@Controller("api/v1/scenarios")
export class ScenarioController {
  constructor(private readonly scenarioService: ScenarioService) {}

  @Get()
  async findAll() {
    return this.scenarioService.findAll();
  }
}
