using Microsoft.EntityFrameworkCore;

namespace CalendarService.DotNet.Data;

public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    public DbSet<User> Users { get; set; }
    public DbSet<ConnectedAccount> ConnectedAccounts { get; set; }
}