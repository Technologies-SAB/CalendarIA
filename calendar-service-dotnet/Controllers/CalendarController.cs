using CalendarService.DotNet.Models;
using CalendarService.DotNet.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Identity.Web;
using Microsoft.Identity.Web.Resource;
using System.Security.Claims;

namespace CalendarService.DotNet.Controllers;

[Authorize(AuthenticationSchemes = "WebApi")]
[ApiController]
[Route("[controller]")]
public class CalendarController : ControllerBase
{
    private readonly IOutlookCalendarService _calendarService;

    public CalendarController(IOutlookCalendarService calendarService)
    {
        _calendarService = calendarService;
    }

    [HttpPost("agendar")]
    public async Task<IActionResult> AgendarEvento([FromBody] EventInput eventInput)
    {
        try
        {
            var userPrincipalName = User.FindFirstValue("preferred_username");

            if (string.IsNullOrEmpty(userPrincipalName))
            {
                return Unauthorized("Não foi possível identificar o usuário a partir do token.");
            }

            var createdEvent = await _calendarService.CreateEventAsync(userPrincipalName, eventInput);
            
            return Ok(new 
            { 
                provider = "outlook", 
                status = "success", 
                message = $"Evento '{createdEvent.Subject}' agendado com sucesso no Outlook." 
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { provider = "outlook", status = "error", message = ex.Message });
        }
    }
}